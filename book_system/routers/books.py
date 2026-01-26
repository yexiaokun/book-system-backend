from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import select, delete, desc, update
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime

from database import get_session
from models import Book, User, BorrowHistory
from worker import generate_pdf_and_send_email, log_operation
from dependencies import get_current_user
from schemas import BookCreate, StandardResponse

router = APIRouter(prefix="/books", tags=["书籍管理"])


@router.post("/", response_model=StandardResponse[Book])
async def create_book(book_in: BookCreate,
          session: AsyncSession = Depends(get_session),
          current_user: User = Depends(get_current_user)
          ):
    print(f"{current_user.username}正在创建图书...")
    book_data = book_in.model_dump()
    new_book = Book(
        **book_data,
        owner_id=current_user.id
    )
    session.add(new_book)
    await session.commit()
    await session.refresh(new_book)

    return StandardResponse(data=new_book)

@router.get("/", response_model=StandardResponse[List[Book]])
async def get_all_books(session: AsyncSession = Depends(get_session)):
    books_data = select(Book)
    result = await session.exec(books_data)
    books = result.all()
    return StandardResponse(data=books)

@router.get("/{book_id}", response_model=StandardResponse[Book])
async def get_one_book(book_id: int, session: AsyncSession = Depends(get_session)):
    book = await session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="找不到这本书")
    return StandardResponse(data=book)

@router.patch("/{book_id}/borrow", response_model=StandardResponse[Book])
async def borrow_book(book_id: int,
                      session: AsyncSession = Depends(get_session),
                      current_user: User = Depends(get_current_user)
                      ):
    book = await session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="库里暂时没有这本书")
    
    statement = (
        update(Book)
        .where(Book.id == book_id)
        .where(Book.count > 0)
        .values(count=Book.count - 1)
    )
    result = await session.exec(statement)
    
    if result.rowcount == 0:
        await session.rollback()
        raise HTTPException(status_code=400, detail="手慢了，库存不足！")
    new_history = BorrowHistory(
        user_id=current_user.id,
        book_id=book_id
    )
    session.add(new_history)
    await session.commit()
    await session.refresh(book)
    generate_pdf_and_send_email.delay(book.title)
    return StandardResponse(data=book)


@router.patch("/{book_id}/return", response_model=StandardResponse[Book])
async def return_book(book_id: int,
                      session: AsyncSession = Depends(get_session),
                      current_user: User = Depends(get_current_user)
                      ):
    book = await session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="书没找到")
    
    statement = (
        select(BorrowHistory)
        .where(BorrowHistory.book_id == book_id)
        .where(BorrowHistory.user_id == current_user.id)
        .where(BorrowHistory.return_date == None)
        .order_by(desc(BorrowHistory.borrow_date))
    )

    result = await session.exec(statement)
    history_record = result.first()
    if not history_record:
        raise HTTPException(status_code=400, detail="你没有借阅这本书，或已归还")
    print(f"🔥 用户 {current_user.username} 正在归还历史记录 ID: {history_record.id}")
    history_record.return_date = datetime.now()

    book.count += 1
    session.add(book)
    

    await session.commit()
    await session.refresh(book)
    log_operation.delay(book.title)
    return StandardResponse(data=book)


@router.delete("/{book_id}", response_model=StandardResponse)
async def delete_book(book_id: int,
                session: AsyncSession = Depends(get_session),
                current_user: User = Depends(get_current_user)
                ):
    print(f"👮‍♂️ 操作者是: {current_user.username}")
    book = await session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="书没找到")
    if book.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="你不是作者，不可以删除这本书！")
    
    statement = (
        select(BorrowHistory)
        .where(BorrowHistory.book_id == book_id)
        .where(BorrowHistory.return_date == None)
    )
    result = await session.exec(statement)
    unreturned_record = result.first()

    if unreturned_record:
        raise HTTPException(
            status_code=400,
            detail="无法删除:该书仍有未归还记录，请等待所有书籍归还后再试"
        )

    delete_statement = delete(Book).where(Book.id == book_id)
    await session.exec(delete_statement)
    print(f"🔥 正在执行删除提交: {book.title}")
    await session.commit()
    return StandardResponse(message=f"成功删除《{book.title}》")