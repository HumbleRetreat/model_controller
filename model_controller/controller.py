from typing import List, Optional, Type, TypeVar, Union, Collection

from pydantic import BaseModel
from sqlalchemy.orm import Session

from model_controller.exception import ControllerException

ORMModel = TypeVar("ORMModel")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class ModelController:
    """Base interface for CRUD operations."""

    def __init__(self, model: Type[ORMModel]) -> None:
        """Initialize the CRUD repository.

        Parameters:
            model (Type[ORMModel]): The ORM model to use for CRUD operations.
        """
        self._model = model
        self._name = model.__name__
        self._polymorph_on = self._get_polymorph_on()
        self._processors = []

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

    def register_processor(self, processor):
        self._processors.append(processor)

    def notify_processors(self, model: Type[ORMModel], data: Union[CreateSchemaType, UpdateSchemaType] = None):
        for processor in self._processors:
            processor.process(model, data)

    def get_one(self, db: Session, *args, **kwargs) -> Optional[ORMModel]:
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
        return db.query(self._model).filter(*args).filter_by(**kwargs).first()

    def get_many(
            self, db: Session, *args, skip: int = 0, limit: int | None = None, **kwargs
    ) -> Collection[ORMModel]:
        """
        Retrieves multiple records from the database.

        Parameters:
            db (Session): The database session.
            *args: Variable number of arguments. For example: filter
                db.query(MyClass).filter(MyClass.name == 'some name', MyClass.id > 5)
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to retrieve.
                Defaults to 100.
            **kwargs: Variable number of keyword arguments. For example: filter_by
                db.query(MyClass).filter_by(name='some name', id > 5)

        Returns:
            List[ORMModel]: List of retrieved records.
        """
        query = db.query(self._model)

        if limit is not None:
            return query.filter(*args).filter_by(**kwargs).offset(skip).limit(limit).all()
        else:
            return query.filter(*args).filter_by(**kwargs).offset(skip).all()

    def create(self, db: Session, obj_create: CreateSchemaType) -> ORMModel:
        """
        Create a new record in the database and return the newly created object.
        If the object has a 'type' field, it will be used to determine the correct
        polymorphic model to instantiate.

        Parameters:
            db (Session): The database session.
            obj_create (CreateModelType): The data for creating the new record.
            It's a pydantic BaseModel

        Returns:
            ORMModel: The newly created record.
        """
        model_class = self._get_actual_model(obj_create)
        obj_create_data = obj_create.model_dump(exclude_none=True, exclude_unset=True)

        db_obj = model_class(**obj_create_data)

        db.add(db_obj)
        db.flush()

        self.notify_processors(model_class, obj_create)

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
        return True