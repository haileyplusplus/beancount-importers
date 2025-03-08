import beangulp
from beangulp.importers import csvbase


class AccountParser(csvbase.Column):
    def __init__(self, *args):
        super().__init__(*args)
        self.account_map = {}

    def parse(self, value):
        value = value.strip()
        return self.account_map[value]

    def set_account_map(self, account_map):
        self.account_map = account_map


class CustomImporter(csvbase.Importer):
    date = csvbase.Date('Date', '%m/%d/%Y')
    narration = csvbase.Columns('Description')
    amount = csvbase.Amount('Amount', subs={
            r'\((.*)\)': r'-\1',
            r'\$': ''}
        )
    account = AccountParser('Account')

    def identify(self, filepath):
        with open(filepath) as fh:
            for line in fh:
                return line.startswith('"Date","Description","Institution"')

    def parse_params(self, importer_params):
        for param in importer_params:
            mapped = param.get('mapped_account')
            if not mapped:
                continue
            # TODO: handle account-specific currency mappings
            self.account_mappings[mapped['importer_account_name']] = mapped['account']

    def __init__(self, account, currency, importer_params):
        self.account_mappings = {}
        self.parse_params(importer_params)
        self.columns['account'].set_account_map(self.account_mappings)
        super().__init__(account, currency)


def get_importer(account, currency, importer_params):
    return CustomImporter(account, currency, importer_params)


if __name__ == "__main__":
    importer_params = {}
    ingest = beangulp.Ingest([get_importer("Assets:Monzo:Cash", "GBP", importer_params)], [])
    ingest()
