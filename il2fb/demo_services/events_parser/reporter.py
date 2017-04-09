# coding: utf-8

from il2fb.github.bug_reporter import BugReporter


def setup_reporter(app, loop):

    reporter = BugReporter(
        loop=loop,
        access_token=app['config']['github']['access_token'],
        repo_owner=app['config']['github']['repo_owner'],
        repo_name=app['config']['github']['repo_name'],
    )

    async def on_shutdown(app):
        reporter.clean_up()

    app['bug_reporter'] = reporter
    app.on_shutdown.append(on_shutdown)

    loop.run_until_complete(reporter.ensure_labels_exist())
