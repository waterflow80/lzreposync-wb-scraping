from typing import List
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from sqlalchemy import create_engine, insert, text
import time

time.sleep(5)  # waiting for required packages to load and get initialized

repos_info_file_location = "./repositories.txt"  # The file that contains information about the packages
distro = "focal"  # The linux distro of which we'll be downloading the packages
depth = 100  # The number of packages to look for
ubuntu_repository_url = "https://packages.ubuntu.com/"
postgres_user = "postgres"  # change it to your db username
postgres_pass = "postgres"
container_ip = "127.0.0.1"

def get_repositories() -> dict:
    """
    Parse the repositories.txt file and retrieve the list of
    repositories to look for
    :return: a dict with the repository name as key and the url as value
    """
    repos_dict = {}
    with open(repos_info_file_location) as repos_file:
        repos = repos_file.readlines()
        for repo in repos:
            repos_dict[repo.split(" ")[0]] = repo.split(" ")[1]
    return repos_dict


def fetch_packages_metadata_from_ubuntu_repository_under_distro_and_section(url: str, section: str = "mail/"):
    url = urljoin(url, section)
    repo_resp = requests.get(url)
    print("INFO: looking IN url:", url)
    repo_soup = BeautifulSoup(repo_resp.content, "html.parser")
    packages_metadata = []
    # Parsing package_name, version and repository
    dts = repo_soup.find_all("dt")
    if dts:
        for dt in dts:
            try:
                package_description = "No description available"
                package_name = dt.a.text
                package_version = dt.text.split(" ")[1]
                repository = dt.text.split(" ")[2]
                #  Parsing package_description
                dd = dt.find_next_sibling("dd")
                if dd:
                    package_description = dd.text
                else:
                    print("WARNING: couldn't find package description")
                packages_metadata.append({
                    "pkgName": package_name,
                    "pkgVersion": package_version,
                    "pkgRepository": repository,
                    "pkgDescription": package_description
                })
            except IndexError:
                #  Some repos don't have version and/or repository attribute
                pass
    else:
        print("WARNING: couldn't find dts")
        raise

    return packages_metadata


def fetch_packages_metadata_from_ubuntu_repository(url: str, distro: str = distro) -> List[dict]:
    """Fetch packages' metadata from the given repository under the given distribution"""
    repo_resp = requests.get(url)
    repo_soup = BeautifulSoup(repo_resp.content, "html.parser")
    ul_distros = repo_soup.find("ul")
    repo_packages_metadata = []
    if ul_distros:
        li_elements = ul_distros.find_all("li")
        for li in li_elements:
            a_tag = li.find("a")
            if a_tag:
                if "focal" in a_tag.text:
                    repo_packages_metadata.extend(
                        fetch_packages_metadata_from_ubuntu_repository_under_distro_and_section(urljoin(url, "/focal/")))
                    break  # Currently we're testing on one repo under one distro and one section
            else:
                print("WARNING: No a_tag found under <li> element")
    else:
        print("WARNING: No ul_element found")
    return repo_packages_metadata


def fetch_all_packages_metadata() -> List[dict]:
    repos_dict = get_repositories()
    all_packages_meta_data = []  # List of dicts (the full list of the packages' metadata)
    for repo_name in repos_dict:
        if repo_name == "ubuntu":
            packages_metadata = fetch_packages_metadata_from_ubuntu_repository(repos_dict[repo_name])
        break  # we're currently processing only packages from debian repos
    all_packages_meta_data.extend(packages_metadata)
    return all_packages_meta_data


def get_db_instance():
    #  Init db and return connection instance
    engine = create_engine("postgresql+psycopg2://%s:%s@%s:5432/DB" % (postgres_user, postgres_pass, container_ip))
    conn = engine.connect()
    return conn

def save_package_metadata(pkg_metadata:dict, conn):
    query = text("INSERT INTO package_meta_data (pkg_name, pkg_version, pkg_description, pkg_repository) VALUES ("
                 "'%s', '%s', '%s', '%s');" % (pkg_metadata["pkgName"], pkg_metadata["pkgVersion"],
                                               pkg_metadata["pkgDescription"], pkg_metadata["pkgRepository"]))
    conn.execute(query)
    conn.commit()


if __name__ == "__main__":
    conn = get_db_instance()
    packages_metadata = fetch_all_packages_metadata()
    for package_md in packages_metadata:
        save_package_metadata(package_md, conn)
