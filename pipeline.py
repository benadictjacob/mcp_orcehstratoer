import requests
from pydantic import BaseModel
from typing import List
import os, zipfile, re, sys
from pathlib import Path


class RepoResult(BaseModel):
    name: str
    owner: str
    url: str
    stars: int
    description: str | None


def clean_readme_preview(text: str) -> str:
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    text = re.sub(r"<img[^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    text = text.replace("#", "").replace("*", "").replace(">", "")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return "\n".join(lines[:20])


def search_github_repos(query: str) -> List[RepoResult]:
    r = requests.get(
        "https://api.github.com/search/repositories",
        params={"q": query}
    )
    if r.status_code != 200:
        return []

    return [
        RepoResult(
            name=i["name"],
            owner=i["owner"]["login"],
            url=i["html_url"],
            stars=i["stargazers_count"],
            description=i.get("description"),
        )
        for i in r.json().get("items", [])
    ]


def repo_readme_text(owner: str, repo: str) -> str:
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/readme")
    if r.status_code != 200:
        return ""
    return requests.get(r.json()["download_url"]).text


def download_repo_zip(owner: str, repo: str, branch="main"):
    base = Path("repo")
    base.mkdir(exist_ok=True)
    target = base / repo
    zip_path = target.with_suffix(".zip")

    os.makedirs(target, exist_ok=True)

    print(f"Downloading {owner}/{repo}", file=sys.stderr)

    r = requests.get(
        f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
    )
    if r.status_code != 200:
        return False

    zip_path.write_bytes(r.content)

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(target)

    return True
