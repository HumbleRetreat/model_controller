from collections.abc import Collection
from contextlib import contextmanager
from typing import Type, Union, Optional

from sqlalchemy.orm import Session

from model_controller.enums import OperationType
from model_controller.exception import ControllerException
from model_controller.filters import FiltersBase
from model_controller.processors.base import ProcessorBase
from model_controller.types import ORMModel, CreateSchemaType, UpdateSchemaType, MutationType


class ModelController:
    """Base interface for CRUD operations."""

    def __init__(self, model: Type[ORMModel], paginate: bool = False) -> None:
        """Initialize the CRUD repository.

        Parameters:
            model (Type[ORMModel]): The ORM model to use for CRUD operations.
            paginate (bool): Enable pagination for the controller.
        """
        self._model = model
        self._name = model.__name__
        self._polymorph_on = self._get_polymorph_on()
        self._processors: list[ProcessorBase] = []

        if paginate:
            try:
                from fastapi_pagination.ext.sqlalchemy import paginate as paginate_sqlalchemy
                self.pagination_method = paginate_sqlalchemy
            except ImportError:
                raise ImportError("To use pagination, you must install `fastapi_pagination`.")
        else:
            self.pagination_method = None

        self.context: dict = {}

    @contextmanager
    def set_context(self, context: dict):
        """
        Context manager to set and reset the context.
        """
        self.context = context
        try:
            yield
        finally:
            self.context = {}

    def _get_polymorph_on(self) -> str | None:
        """
        Check if the model is polymorphic and return the polymorphic_on attribute.
        Return `None` if the model is not polymorphic.

        Returns:
            str | None: The polymorphic_on attribute of the model.
        """
        mapper_args = getattr(self._model, '__mapper_args__', None)
        if mapper_args:
            return mapper_args.get('polymorphic_on', None)

        return None

    def _get_actual_model(self, data: CreateSchemaType) -> Type[ORMModel]:
        """
        Get the actual model to be used for creating the object. For non-polymorphic models,
        this will be the model passed to the controller. For polymorphic models, this will be
        the subclass of the model that corresponds to the polymorphic identity of the object.

        Parameters:
            data (dict[str, str]): The data to be used for creating the object.

        Returns:
            Type[ORMModel]: The actual model to be used for creating the object.
        """
        if not self._polymorph_on:
            return self._model

        data_has_identity = getattr(data, self._polymorph_on, None)

        if self._polymorph_on and data_has_identity:
            for subclass in self._model.__subclasses__():
                if subclass.__mapper_args__.get('polymorphic_identity') == data_has_identity:
                    return subclass

        raise ControllerException(f"Cannot resolve the actual model for {self._name}")

    def register_processor(self, processor: ProcessorBase):
        self._processors.append(processor)

    def _notify_processors(self, operation: OperationType, model: Type[ORMModel],
                           data: Optional[MutationType]):
        """
        Notify all registered processors about the operation.

        Parameters:
            operation (OperationType): The operation type.
            model (Type[ORMModel]): The model class.
            data (Union[CreateSchemaType, UpdateSchemaType, None]): The data for the operation.
        """
        for processor in self._processors:
            processor.process(operation, model, data, self.context)

    def get_one(self, db: Session, *args, **kwargs) -> ORMModel | None:
        """
        Retrieves one record from the database.

        Parameters:
            db (Session): The database session object.
            *args: Variable length argument list used for filter
                e.g. filter(MyClass.name == 'some name')
            **kwargs: Keyword arguments used for filter_by e.g.
                filter_by(name='some name')

        Returns:
            Optional[ORMModel]: The retrieved record, if found.
        """
        return db.query(self._model).where(*args).filter_by(**kwargs).first()

    def get_many(
            self, db: Session, filters: FiltersBase | None = None, *args, **kwargs
    ) -> Collection[ORMModel]:
        """
        Retrieves multiple records from the database.

        Parameters:
            db (Session): The database session.
            filters (FiltersBase): The filters to apply to the query.
            *args: Variable number of arguments. For example: filter
                db.query(MyClass).filter(MyClass.name == 'some name', MyClass.id > 5)
            **kwargs: Variable number of keyword arguments. For example: filter_by
                db.query(MyClass).filter_by(name='some name', id > 5)

        Returns:
            List[ORMModel]: List of retrieved records.
        """
        query = db.query(self._model).filter(*args).filter_by(**kwargs)

        # Dynamically apply filters from the filters class
        if filters:
            filters_dict = filters.model_dump(exclude_unset=True, exclude_none=True)
            for field, value in filters_dict.items():
                if field.endswith('_lt'):
                    query = query.filter(getattr(self._model, field[:-3]) < value)
                elif field.endswith('_gt'):
                    query = query.filter(getattr(self._model, field[:-3]) > value)
                elif field.endswith('_like'):
                    query = query.filter(getattr(self._model, field[:-5]).like(f"%{value}%"))
                else:
                    query = query.filter(getattr(self._model, field) == value)

        if self.pagination_method:
            return self.pagination_method(db, query)

        self._notify_processors(OperationType.READ, self._model, filters)

        return query.all()

    def create(self, db: Session, obj_create: CreateSchemaType) -> ORMModel:
        """
        Create a new record in the database and return the newly created object.
        If the object has a 'type' field, it will be used to determine the correct
        polymorphic model to instantiate.

        Parameters:
            db (Session): The database session.
            obj_create (CreateModelType): The data for creating the new record.

        Returns:
            ORMModel: The newly created record.
        """
        model_class: Type[ORMModel] = self._get_actual_model(obj_create)
        obj_create_data = obj_create.model_dump(exclude_none=True, exclude_unset=True)

        db_obj = model_class(**obj_create_data)

        db.add(db_obj)
        db.flush()

        self._notify_processors(OperationType.CREATE, model_class, obj_create)

        return db_obj

    def update_object(
            self,
            db: Session,
            db_obj: ORMModel,
            obj_update: UpdateSchemaType,
    ) -> ORMModel:
        """
        Updates a record in the database.

        Parameters:
            db (Session): The database session.
            db_obj (ORMModel): The database object to be updated.
            obj_update (UpdateModelType): The updated data for the object
                - it's a pydantic BaseModel.

        Returns:
            ORMModel: The updated database object.
        """
        obj_update_data = obj_update.model_dump(
            exclude_unset=True
        )

        for field, value in obj_update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.flush()

        self._notify_processors(OperationType.UPDATE, type(db_obj), obj_update)

        return db_obj

    def delete(self, db: Session, db_obj: ORMModel) -> bool:
        """
        Deletes a record from the database.

        Parameters:
            db (Session): The database session.
            db_obj (ORMModel): The object to be deleted from the database.

        Returns:
            ORMModel: The deleted object.

        """
        db.delete(db_obj)
        db.flush()

        self._notify_processors(OperationType.DELETE, type(db_obj), db_obj)

        return True
