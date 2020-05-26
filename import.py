import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


DATABASE_URL = "postgres://joqityswncejjo:ce560d2222c9edcc16f30e8f95c840a7d8348c8bef7ca3b351ecdb32c63e3f48@ec2-54-86-170-8.compute-1.amazonaws.com:5432/d7s7d50npqadm9"

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    next(reader, None)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added book {title} by {author} isbn {isbn} from the year {year}.")
    db.commit()

if __name__ == "__main__":
    main()
