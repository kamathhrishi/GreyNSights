import yaml
from .analyst import Command


class Config:
    def __init__(self, owner):

        self.file = None
        self.approval = None
        self.name = owner.name
        self.host = owner.host
        self.port = owner.port

    def load(self, path):

        fp = open(path, "r")
        self.file = yaml.load(fp)

        for value in self.file.keys():

            setattr(self, value, self.file[value])

        return self.file

    def __str__(self):

        string = "\n"
        string += "\n"
        string += "owner_name: " + self.file["owner_name"]
        string += "\n"
        string += "dataset_name: " + self.file["dataset_name"]
        string += "\n"
        string += "privacy_budget: " + str(self.file["privacy_budget"])
        string += "\n"
        string += "trusted-aggregator: " + self.file["trusted_aggregator"]
        string += "\n"
        string += "secret-sharing: " + self.file["secret_sharing"]
        string += "\n"
        string += "private_columns: "
        string += "\n"
        string += "\n"
        for i in range(0, len(self.file["private_columns"])):

            string += "\t" + "-" + self.file["private_columns"][i]
            string += "\n"

        string += "visible_columns: "
        string += "\n"
        string += "\n"
        for i in range(0, len(self.file["visible_columns"])):

            string += "\t" + "-" + self.file["visible_columns"][i]
            string += "\n"

        string += "restricted_columns: "
        string += "\n"
        string += "\n"
        for i in range(0, len(self.file["restricted_columns"])):

            string += "\t" + "-" + self.file["restricted_columns"][i]
            string += "\n"

        string += "allowed_queries: "
        string += "\n"
        string += "\n"
        for i in range(0, len(self.file["restricted_columns"])):

            string += "\t" + "-" + self.file["restricted_columns"][i]
            string += "\n"
        string += "restricted_columns: "
        string += "\n"
        string += "\n"
        for i in range(0, len(self.file["restricted_columns"])):

            string += "\t" + "-" + self.file["restricted_columns"][i]
            string += "\n"

        string += "visible_queries: "
        string += "\n"
        string += "\n"
        for i in range(0, len(self.file["visible_queries"])):

            string += "\t" + "-" + self.file["visible_queries"][i]
            string += "\n"

        string += "restricted_queries: "
        string += "\n"
        string += "\n"
        for i in range(0, len(self.file["restricted_queries"])):

            string += "\t" + "-" + self.file["restricted_queries"][i]
            string += "\n"

        return string

    def init_pointer(self):

        """Initialized pointer from the hosted dataset.

        Returns:
            returned_pt[Pointer]: The returned pointer"""

        if self.approval:

            self.additional_data = {"name": self.name}

            cmd = Command(
                self.host,
                self.port,
                "init_query",
                additional_data=self.additional_data,
            )
            returned_msg = cmd.execute("init")
            returned_pt = returned_msg.data
            returned_pt.hook()
            return returned_pt

        else:

            raise Exception("LOL")

    def approve(self):
        self.approval = True
        return self

    def reject(self):
        self.approval = False
        return self


# config = Config()
# var = config.load("test_config.yaml")
