def get_next_month(date_str):
    date_object = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    next_month = date_object + datetime.timedelta(days=31)
    next_month = next_month.replace(day=min(next_month.day, date_object.day))

    next_month_str = next_month.strftime("%Y-%m-%d")

    return next_month_str
