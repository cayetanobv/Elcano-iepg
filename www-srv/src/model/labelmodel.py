# coding=UTF8

"""

Label model.

"""
from base.PostgreSQL.PostgreSQLModel import PostgreSQLModel


class LabelModel(PostgreSQLModel):
    """Model for labels."""

    def getLabels(self, lang="es"):
        """Returns labels in the given language."""
        if lang=="es":
            q = "select id_label_es as id, label from www.label_es;"
        if lang=="en":
            q = "select id_label_en as id, label from www.label_en;"

        return self.query(q).result()


    def insertLabel(self, label, lang="es"):
        """Inserts a label."""
        if lang=="es":
            return self.insert("www.label_es", {"label": label}, "id_label_es")
        if lang=="en":
            return self.insert("www.label_en", {"label": label}, "id_label_en")
