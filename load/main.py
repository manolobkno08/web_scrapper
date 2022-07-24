from base import Base, Engine, Session
from article import Article
import pandas as pd
import argparse
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(filename):
    """ Load data """
    Base.metadata.create_all(Engine)  # Generate schema
    session = Session()
    articles = pd.read_csv(filename)

    # Iter into dataframe
    for index, row in articles.iterrows():
        logger.info("Loading article uid {} into DB".format(row['uid']))
        article = Article(row['uid'],
                          row['body'],
                          row['host'],
                          row['newspaper_uid'],
                          row['url'])

        session.add(article)
    session.commit()
    session.close()


if __name__ == '__main__':
    """ Entry point """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'filename', help='The file you want to load into DB', type=str)
    args = parser.parse_args()

    main(args.filename)
