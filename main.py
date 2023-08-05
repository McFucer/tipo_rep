from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel


app = FastAPI()


SQLALCHEMY_DATABASE_URL = "sqlite:///./messenger.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    global db
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    password = Column(Integer)
    comments = relationship("Comment", back_populates="user")



class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    comment = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="comments")



Base.metadata.create_all(engine)



class UserCreate(BaseModel):
    name: str
    email: str
    password: str



class CommentCreate(BaseModel):
    comment: str
    user_id: int



class UserSchema(BaseModel):
    id: int
    name: str
    email: str



class CommentSchema(BaseModel):
    id: int
    comment: str
    user_id: int



@app.post("/users/", response_model=UserSchema)
async def create_user(user: UserCreate,db: Session = Depends(get_db)):
    db_user = User(name=user.name, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



@app.get("/users/", response_model=list[UserSchema])
async def get_users(db=Depends(get_db)):
    users = db.query(User).all()
    return users



@app.get("/users/{user_id}", response_model=UserSchema)
async def get_user(user_id: int, db=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user



@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}



@app.post("/comments/", response_model=CommentSchema)
async def create_comment(comment: CommentCreate, db=Depends(get_db)):
    db_comment = Comment(comment=comment.comment, user_id=comment.user_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment



@app.get("/users/{user_id}/comments/", response_model=list[CommentSchema])
async def get_comments_by_user(user_id: int, db=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.comments



@app.put("/comments/{comment_id}")
async def update_comment(comment_id: int, comment: str, db=Depends(get_db)):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    db_comment.comment = comment
    db.commit()
    db.refresh(db_comment)
    return db_comment

