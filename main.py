
import urllib.request
import urllib.error
import json
from datetime import datetime


def get_json(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def main():
    with open("requirements.txt", "r", encoding="utf-8") as file:
        lines = [
            line.strip()
            for line in file
            if line.strip() and not line.strip().startswith("#")
        ]

    checked = 0
    packages_missing = 0
    versions_missing = 0
    valid_releases = []

    for line in lines:
        checked += 1

        if "==" not in line:
            continue

        name, version = line.split("==", 1)
        name = name.strip()
        version = version.strip()

        try:
            package_data = get_json(
                f"https://pypi.org/pypi/{name}/json"
            )

            if package_data is None:
                packages_missing += 1
                continue

            release_data = get_json(
                f"https://pypi.org/pypi/{name}/{version}/json"
            )

            if release_data is None:
                versions_missing += 1
                continue

            urls = release_data.get("urls", [])

            if not urls:
                continue

            upload_time = urls[0].get("upload_time")

            if upload_time:
                year = datetime.fromisoformat(
                    upload_time.replace("Z", "+00:00")
                ).year

                valid_releases.append(
                    (upload_time, name, version, year)
                )

        except Exception as e:
            print(f"Error checking {name}: {e}")

    print(f"Dependencies checked: {checked}")
    print(f"Packages not on PyPI: {packages_missing}")
    print(f"Versions not on PyPI: {versions_missing}")

    if valid_releases:
        oldest = min(valid_releases, key=lambda item: item[0])
        _, name, version, year = oldest

        print(
            f"Oldest pinned release: {name}=={version} ({year})"
        )
    else:
        print("Oldest pinned release: None")


if __name__ == "__main__":
    main()
