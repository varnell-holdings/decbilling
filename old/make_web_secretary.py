def make_web_secretary_from_shelf(today_path):
    """Render jinja2 template
    and write to file for web page of today's patients
    from shelf data
    """
    today_str = today.strftime("%A" + "  " + "%d" + "-" + "%m" + "-" + "%Y")

    with shelve.open(str(today_path)) as s:
        today_data = list(s.values())

    today_data.sort(key=lambda x: x["out_theatre"], reverse=True)

    path_to_template = epdata_path
    loader = FileSystemLoader(path_to_template)
    env = Environment(loader=loader)
    template_name = "web_sec_template.html"
    template = env.get_template(template_name)
    a = template.render(today_data=today_data, today_date=today_str)
    with open(sec_web_page, "w", encoding="utf-8") as f:
        f.write(a)
