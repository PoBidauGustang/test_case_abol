import os
import time

import books_pb2
import books_pb2_grpc
import grpc
from flask import Flask, jsonify

app = Flask(__name__)


def get_grpc_client():
    retries = 5
    while retries > 0:
        try:
            channel = grpc.insecure_channel(
                f'{os.getenv("GRPC_SERVER_HOST")}:{os.getenv("GRPC_SERVER_PORT")}'
            )
            grpc.channel_ready_future(channel).result(timeout=10)
            client = books_pb2_grpc.BookServiceStub(channel)
            return client
        except grpc.FutureTimeoutError:
            retries -= 1
            print(f"gRPC server not ready, retrying... ({5 - retries}/5)")
            time.sleep(2)


@app.route("/books/<book_uuid>", methods=["GET"])
def get_book(book_uuid):
    try:
        client = get_grpc_client()
        response = client.GetBookById(books_pb2.BookIdRequest(uuid=book_uuid))
        return jsonify(
            {
                "uuid": response.uuid,
                "title": response.title,
                "author": response.author,
                "published_date": response.published_date,
            }
        )
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), e.code().value[0]


@app.route("/books", methods=["GET"])
def get_all_books():
    try:
        client = get_grpc_client()
        response = client.GetAllBooks(books_pb2.Empty())
        books = [
            {
                "uuid": book.uuid,
                "title": book.title,
                "author": book.author,
                "published_date": book.published_date,
            }
            for book in response.books
        ]
        return jsonify(books)
    except grpc.RpcError as e:
        return jsonify({"error": e.details()}), e.code().value[0]


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
