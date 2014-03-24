# coding=UTF8

"""

Label model.

"""
from base.PostgreSQL.PostgreSQLModel import PostgreSQLModel
import helpers


class LabelModel(PostgreSQLModel):
    """Model for labels."""
    def getLabels(self, lang):
        """Returns labels in the given language."""
        helpers.checkLang(lang)
        q = "select id_label_{} as id, label from www.label_{};".format(lang, lang)
        return self.query(q).result()


    def insertLabel(self, label, lang="es"):
        """Inserts a label."""
        helpers.checkLang(lang)
        return self.insert("www.label_{}".format(lang), {"label": label}, "id_label_{}".format(lang))
