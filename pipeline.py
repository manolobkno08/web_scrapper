import subprocess
import logging
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
news_sites_uids = ['eluniversal', 'elpais']


def main():
    _extract(news_sites_uids)
    _transform()
    _load()


def _extract(news_sites_uids):
    """ Extract data """
    logger.info("Starting extraction process")
    for news_site_uid in news_sites_uids:
        subprocess.run(['python3', 'main.py', news_site_uid], cwd='./extract')
        subprocess.run(['find', '.', '-name', '{}*'.format(news_site_uid), '-exec', 'mv',
                       '{}', '../transform/{}_.csv'.format(news_site_uid), ';'], cwd='./extract')


def _transform():
    """ Transform dataframes """
    logger.info("Starting transform process")
    for news_site_uid in news_sites_uids:
        dirty_data_filename = '{}_.csv'.format(news_site_uid)
        clean_data_filename = 'clean_{}'.format(dirty_data_filename)
        subprocess.run(
            ['python3', 'main.py', dirty_data_filename], cwd='./transform')
        subprocess.run(['rm', dirty_data_filename], cwd='./transform')
        subprocess.run(['mv', clean_data_filename,
                       '../load/{}.csv'.format(news_site_uid)], cwd='./transform')


def _load():
    """ Save data into DB """
    logger.info("Starting load process")
    for news_site_uid in news_sites_uids:
        clean_data_filename = '{}.csv'.format(news_site_uid)
        subprocess.run(
            ['python3', 'main.py', clean_data_filename], cwd='./load')
        subprocess.run(['rm', clean_data_filename], cwd='./load')


if __name__ == '__main__':
    main()
