import pandas as pd
from urllib.parse import urlparse
import argparse
import hashlib
import logging
logging.basicConfig(level=logging.INFO)


logger = logging.getLogger(__name__)


def main(filename):
    """ Build DataFrame """
    logger.info("Starting cleaning process...")
    # Create dataframe
    df = _read_data(filename)
    newspaper_uid = _extract_newspaper_uid(filename)
    df = _add_newspaper_uid_column(df, newspaper_uid)
    df = _extract_host(df)
    df = _fill_missing_titles(df)
    df = _generate_uids_for_rows(df)
    df = _remove_new_lines_from_body(df)
    df = _remove_duplicates(df, 'title')
    df = _drop_rows_with_missing_values(df)

    _save_data(df, filename)

    return df


def _read_data(filename):
    """ Read CSV file """
    logger.info("Reading file {}".format(filename))
    return pd.read_csv(filename)


def _extract_newspaper_uid(filename):
    """ Extract the newspaper_uid """
    logger.info("Extracting newspaper_uid")
    newspaper_uid = filename.split("_")[0]
    logger.info("Newspaper_uid detected: {}".format(newspaper_uid))
    return newspaper_uid


def _add_newspaper_uid_column(df, newspaper_uid):
    """ Adding new column as newspaper_uid """
    logger.info("Filling newspaper_uid column with {}".format(newspaper_uid))
    df['newspaper_uid'] = newspaper_uid
    return df


def _extract_host(df):
    """ Extract host """
    logger.info("Extracting host from urls")
    df['host'] = df['url'].apply(lambda url: urlparse(url).netloc)
    return df


def _fill_missing_titles(df):
    """ Fill missing titles """
    logger.info('Filling missing titles')
    missing_titles_mask = df['title'].isna()
    missing_titles = (df[missing_titles_mask]['url']
                      .str.extract(r'(?P<missing_titles>[^/]+)$')
                      .applymap(lambda title: title.split('-'))
                      .applymap(lambda title_word_list: ' '.join(title_word_list))
                      )
    df.loc[missing_titles_mask, 'title'] = missing_titles.loc[:, 'missing_titles']
    return df


def _generate_uids_for_rows(df):
    """ Generate uids for each news """
    logger.info('Generating uids for each rows')
    uids = (df
            .apply(lambda row: hashlib.md5(bytes(row['url'].encode())), axis=1)
            .apply(lambda hash_object: hash_object.hexdigest())
            )
    # Add uid rows into dataframe
    df['uid'] = uids
    return df.set_index('uid')


def _remove_new_lines_from_body(df):
    """ Remove new lines """
    logger.info('Removing new lines from body')
    stripped_body = (df
                     .apply(lambda row: row['body'], axis=1)  # Get body only
                     .apply(lambda body: list(body))
                     .apply(lambda letters: list(map(lambda letter: letter.replace('\n', ''), letters)))
                     .apply(lambda letters: ''.join(letters))
                     # or just .apply(lambda row: row['body'].replace('\n', ''), axis=1)
                     )
    df['body'] = stripped_body
    return df


def _remove_duplicates(df, column_name):
    """ Remove duplicates """
    logger.info('Removing duplicate records')
    df.drop_duplicates(subset=[column_name], keep='first', inplace=True)
    return df


def _drop_rows_with_missing_values(df):
    """ Drop rows with missing values """
    return df.dropna()


def _save_data(df, filename):
    """ Save final DataFrame """
    clean_filename = 'clean_{}'.format(filename)
    logger.info('Saving data at location: {}'.format(clean_filename))
    df.to_csv(clean_filename, encoding='utf-8-sig')


if __name__ == '__main__':
    """ Entry point and capture argument """
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='The path to the raw data', type=str)

    args = parser.parse_args()
    df = main(args.filename)
    print(df)
