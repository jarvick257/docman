class Date:
    @classmethod
    def add_parser(cls, subparser):
        parser = subparser.add_parser("date", description="Sets the document date.")
        parser.add_argument(
            "date", nargs="*", metavar="YYYY-MM-DD", help="document date"
        )
        parser.add_argument("--today", action="store_true", help="Set to today's date")
        parser.set_defaults(function=cls.run)

    @classmethod
    def run(cls, doc, date=[], today=False, **kwargs):
        import datetime as dt

        if today:
            doc.date = dt.date.now()
            doc.save()
            print(doc.date.date())
            return 0

        if date == []:
            print(doc.date.date())
            return 0

        try:
            # try converting to date to check format
            new_date = "-".join(date).replace(" ", "-")
            # fromisoformat only available in python3.7
            # new_date = str(dt.date.fromisoformat(new_date))
            new_date = dt.datetime.strptime(new_date, "%Y-%m-%d")
        except ValueError:
            try:
                new_date = dt.datetime.strptime(new_date, "%Y%m%d")
            except ValueError:
                print("Date must be in YYYY-MM-DD format.")
                return 1
        doc.date = new_date
        print(doc.date.date())
        doc.save()
        return 0
