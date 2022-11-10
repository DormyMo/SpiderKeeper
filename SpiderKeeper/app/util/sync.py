#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tempfile
import subprocess
from os import path
from git import Repo
from SpiderKeeper.app import agent
from SpiderKeeper.app.spider.model import Project
import logging

logger = logging.getLogger("[GIT SYNC]")

def git_sync(project_id, git_uri, git_folder):
    """

    git_uri: uri pointing to git repo.
    git_folder: path to spider root relative to git_uri
    """
    spider_folder = git_folder.strip('/')
    output_stem = spider_folder if spider_folder else 'test'
    project = Project.find_project_by_id(project_id)
    with tempfile.TemporaryDirectory() as tmp_dir:
        logger.debug(f"cloning from {git_uri} to {tmp_dir}.")
        Repo.clone_from(git_uri, tmp_dir)
        spider_root = path.join(tmp_dir, spider_folder)
        gen_egg(output_stem, spider_root)
        egg_path = path.join(spider_root, f"{output_stem}.egg")
        agent.deploy(project, egg_path)

def gen_egg(output_stem, cwd):
    cmd_lst = ["scrapyd-deploy", "--build-egg", f"{output_stem}.egg"]
    if path.exists(path.join(cwd, "requirements.txt")):
        cmd_lst.append("--include-dependencies")
    logger.debug(f"generating egg file")
    p = subprocess.Popen(cmd_lst, cwd=cwd)
    p.wait()

