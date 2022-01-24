# Copyright (C) 2019-2021  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

MVN_ARTIFACTS = [
    {
        "time": 1626109619335,
        "url": "https://repo1.maven.org/maven2/al/aldi/sprova4j/0.1.0/"
        + "sprova4j-0.1.0.jar",
        "gid": "al.aldi",
        "aid": "sprova4j",
        "filename": "sprova4j-0.1.0.jar",
        "version": "0.1.0",
        "base_url": "https://repo1.maven.org/maven2/",
    },
]


def test_tasks_maven_loader(
    mocker, swh_scheduler_celery_app, swh_scheduler_celery_worker, swh_config
):
    mock_load = mocker.patch("swh.loader.package.maven.loader.MavenLoader.load")
    mock_load.return_value = {"status": "eventful"}

    res = swh_scheduler_celery_app.send_task(
        "swh.loader.package.maven.tasks.LoadMaven",
        kwargs=dict(url=MVN_ARTIFACTS[0]["url"], artifacts=MVN_ARTIFACTS,),
    )
    assert res
    res.wait()
    assert res.successful()
    assert mock_load.called
    assert res.result == {"status": "eventful"}


def test_tasks_maven_loader_snapshot_append(
    mocker, swh_scheduler_celery_app, swh_scheduler_celery_worker, swh_config
):
    mock_load = mocker.patch("swh.loader.package.maven.loader.MavenLoader.load")
    mock_load.return_value = {"status": "eventful"}

    res = swh_scheduler_celery_app.send_task(
        "swh.loader.package.maven.tasks.LoadMaven",
        kwargs=dict(url=MVN_ARTIFACTS[0]["url"], artifacts=[]),
    )
    assert res
    res.wait()
    assert res.successful()
    assert mock_load.called
    assert res.result == {"status": "eventful"}
