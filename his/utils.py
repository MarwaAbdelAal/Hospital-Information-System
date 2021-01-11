from datetime import datetime
import re


def generate_gcalendar_link(title: str, description: str, start: datetime, end: datetime):
    """get_gcalendar_link return a link to google calendar in form of:
    https://www.google.com/calendar/render?action=TEMPLATE&text=title&details=description&location=location&dates=20210111T020200Z%2F20210112T020200Z

    Parameters
    ----------
    title : str
        [description]
    description : str
        [description]
    start : str
        [description]
    end : str
        [description]

    Returns
    -------
    [type]
        [description]
    """
    return f'https://www.google.com/calendar/render?action=TEMPLATE&text={title}&details={description}&dates={re.sub("[-:]", "", start.isoformat()).split(".", 1)[0]}/{re.sub("[-:]", "", end.isoformat()).split(".", 1)[0]}'
