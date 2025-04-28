from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine, Index
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session as OrmSession
from sqlalchemy.orm import sessionmaker
import datetime


Base = declarative_base()


class Session(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace = Column(String, nullable=False)
    assistant = Column(String, nullable=False)
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_workspace_assistant', 'workspace', 'assistant'),
    )


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    content = Column(String, nullable=False)
    role = Column(String, nullable=False)

    session = relationship("Session", back_populates="messages")


def create_orm_session(sqlitepath):
    engine = create_engine(sqlitepath, echo=False) # sqlite:///path_to_your_database.db
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


class ChatSessionRepository:
    
    def __init__(self, db_session: OrmSession):
        self.db_session = db_session

    def create(self, workspace, assistant, messages):
        """
        Crea una nueva sesión y sus mensajes asociados.

        Args:
            workspace (str): Nombre del workspace.
            assistant (str): Nombre del assistant.
            messages (list[dict]): Lista de mensajes, cada uno con 'timestamp', 'content', 'role'.

        Returns:
            Session: La instancia de la sesión creada.
        """
        session_obj = Session(workspace=workspace, assistant=assistant)
        self.db_session.add(session_obj)
        self.db_session.flush()  # Para obtener el id de la sesión

        for msg in messages:
            message_obj = Message(
                session_id=session_obj.id,
                content=msg['content'],
                role=msg['role']
            )
            self.db_session.add(message_obj)

        self.db_session.commit()
        self.db_session.refresh(session_obj)
        return session_obj

    def find_by_workspace_and_assistant(self, workspace, assistant):
        """
        Encuentra sesiones por workspace y assistant.

        Args:
            workspace (str): Nombre del workspace.
            assistant (str): Nombre del assistant.

        Returns:
            list[Session]: Lista de sesiones que coinciden con los criterios.
        """
        return self.db_session.query(Session).filter_by(workspace=workspace, assistant=assistant).first()

    def update(self, session):
        """
        Actualiza una sesión existente en la base de datos.

        Args:
            session (Session): La instancia de la sesión a actualizar.

        Returns:
            Session: La sesión actualizada.
        """
        existing_session = self.db_session.query(Session).filter_by(id=session.id).first()
        if existing_session:
            existing_session.workspace = session.workspace
            existing_session.assistant = session.assistant
            existing_session.messages = session.messages
            self.db_session.commit()
            self.db_session.refresh(existing_session)
            return existing_session
        else:
            raise ValueError("Session not found")
