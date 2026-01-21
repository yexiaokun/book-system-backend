from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select
from typing import List

from database import get_session
from models import Book, BookCreate, User
from worker import generate_pdf_and_send_email, log_operation
from dependencies import get_current_user

router = APIRouter(prefix="/books", tags=["书籍管理"])


@router.post("/", response_model=Book)
def books(book_data: BookCreate,
          session: Session = Depends(get_session),
          current_user: User = Depends(get_current_user)
          ):
    print(f"{current_user}正在创建图书...")
    new_book = Book(
        title=book_data.title,
        price=book_data.price
    )
    new_book.owner_id = current_user.id
    session.add(new_book)
    session.commit()
    session.refresh(new_book)
    print(f"数据已存入数据库，book_id为{new_book.id}，书名为《{new_book.title}》")
    return new_book

@router.get("/", response_model=List[Book])
def get_all_books(session: Session = Depends(get_session)):
    books_data = select(Book)
    books = session.exec(books_data).all()
    return books

@router.get("/{book_id}", response_model=Book)
def get_one_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="找不到这本书")
    return book

@router.patch("/{book_id}/borrow", response_model=Book)
def borrow_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="书没找到")
    book.is_borrowed = True
    session.add(book)
    session.commit()
    session.refresh(book)

    generate_pdf_and_send_email.delay(book.title)
    return book


@router.patch("/{book_id}/return", response_model=Book)
def return_book(book_id: int, session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="书没找到")
    book.is_borrowed = False
    session.add(book)
    session.commit()
    session.refresh(book)

    log_operation.delay(book.title)
    return book


@router.delete("/{book_id}")
def delete_book(book_id: int,
                session: Session = Depends(get_session),
                current_user: User = Depends(get_current_user)
                ):
    book = session.get(Book, book_id)
    print(f"👮‍♂️ 操作者是: {current_user.username}")
    book = session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="书没找到")
    if book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="你不是作者，不可以删除这本书！")
    session.delete(book)
    session.commit()
    return {"msg": f"成功删除id为{book_id}的《{book.title}》"}