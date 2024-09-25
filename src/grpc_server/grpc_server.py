from concurrent import futures

import books_pb2_grpc
import grpc
from books_pb2 import BookResponse, BooksListResponse
from database import get_db
from faststream.rabbit import RabbitBroker
from models import Book
from sqlalchemy.future import select

broker = RabbitBroker("amqp://rabituser:123qwe@rabbitmq:5672/")


class BookService(books_pb2_grpc.BookServiceServicer):
    async def GetBookById(self, request, context):
        database = get_db()
        async with database.get_session() as session:
            result = await session.execute(
                select(Book).filter(Book.uuid == request.uuid)
            )
            book = result.scalar_one_or_none()
            if book:
                return BookResponse(
                    uuid=str(book.uuid),
                    title=book.title,
                    author=book.author,
                    published_date=book.published_date.isoformat(),
                )
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Book not found")
            return BookResponse()

    async def GetAllBooks(self, request, context):
        database = get_db()
        async with database.get_session() as session:
            result = await session.execute(select(Book))
            books = result.scalars().all()
            return BooksListResponse(
                books=[
                    BookResponse(
                        uuid=str(book.uuid),
                        title=book.title,
                        author=book.author,
                        published_date=book.published_date.isoformat(),
                    )
                    for book in books
                ]
            )


@broker.subscriber("book_queue")
async def on_message(body):
    print(f" [x] Received message from RabbitMQ: {body}")


async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    books_pb2_grpc.add_BookServiceServicer_to_server(BookService(), server)
    server.add_insecure_port("[::]:50051")
    await server.start()
    await broker.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    import asyncio

    asyncio.run(serve())
