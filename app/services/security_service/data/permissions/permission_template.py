from sqlalchemy import String, Boolean, Column, Integer, UniqueConstraint

from models import Base


class PermissionTemplate(Base):
    __abstract__ = True

    id: int = Column(Integer, primary_key=True)
    root_permission_id: int | None = Column(Integer, nullable=True)
    permission: str = Column(String, nullable=False)
    permission_name: str = Column(String, nullable=False)
    create: bool = Column(Boolean, default=False, nullable=False)
    read: bool = Column(Boolean, default=False, nullable=False)
    update: bool = Column(Boolean, default=False, nullable=False)
    delete: bool = Column(Boolean, default=False, nullable=False)
    admin: bool = Column(Boolean, default=False, nullable=False)
    parent_id: int = Column(Integer, primary_key=True)

    __table_args__ = (UniqueConstraint("parent_id", "permission"),)

    def update_from_dict(self, item: dict):
        for key, value in item.items():
            if not hasattr(self, key):
                continue
            setattr(self, key, value)

    def to_dict(self, only_actions: bool = False):
        res = self.__dict__
        if "_sa_instance_state" in res:
            res.pop("_sa_instance_state")
            relationships = self.__mapper__.relationships.keys()
            if relationships:
                for relationship in relationships:
                    if relationship in res:
                        res.pop(relationship)
        if only_actions:
            return {
                "create": res["create"],
                "read": res["read"],
                "update": res["update"],
                "delete": res["delete"],
                "admin": res["admin"],
            }
        return res
