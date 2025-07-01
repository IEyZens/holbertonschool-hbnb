# Importation du module de test unitaire intégré à Python
import unittest

# Importation de uuid pour vérifier la validité des identifiants générés
import uuid

# Importation de datetime pour valider les types de dates
from datetime import datetime

# Importation du modèle de base à tester
from app.models.base_model import BaseModel

# Importation de time pour mesurer des différences temporelles
import time


# Définition de la classe de tests pour BaseModel
class TestBaseModel(unittest.TestCase):

    # Teste si une instance de BaseModel peut être créée correctement
    def test_can_create_basemodel_instance(self):
        # Création d'une instance
        obj = BaseModel()

        # Vérifie que c'est bien une instance de BaseModel
        self.assertTrue(isinstance(obj, BaseModel))

        # Vérifie que l'attribut id est une chaîne de caractères
        self.assertIsInstance(obj.id, str)

        # Tente de convertir l'id en UUID pour valider son format
        try:
            uuid_obj = uuid.UUID(obj.id)

            # Vérifie que l'id converti est égal à l'original
            self.assertEqual(str(uuid_obj), obj.id)
        except ValueError:
            # Échec si l'id n'est pas un UUID valide
            self.fail("id is not a valid UUID string")

        # Vérifie que created_at est un objet datetime
        self.assertIsInstance(obj.created_at, datetime)

        # Vérifie que updated_at est un objet datetime
        self.assertIsInstance(obj.updated_at, datetime)

    # Vérifie que chaque instance de BaseModel a un id unique
    def test_each_instance_has_different_id(self):
        # Création de deux instances
        first = BaseModel()
        second = BaseModel()

        # Vérifie que leurs IDs sont différents
        self.assertNotEqual(first.id, second.id)

    # Vérifie que la méthode save met à jour le champ updated_at
    def test_save_method_refreshes_updated_at(self):
        # Création d'une instance
        instance = BaseModel()

        # Sauvegarde de la valeur actuelle de updated_at
        before = instance.updated_at

        # Pause pour permettre un décalage temporel
        time.sleep(0.5)

        # Appel de la méthode save qui doit mettre à jour updated_at
        instance.save()

        # Récupération de la nouvelle valeur
        after = instance.updated_at

        # Vérifie que updated_at a été mis à jour
        self.assertGreater(after, before)

        # Vérifie que l'écart est proche de 0.5s (tolérance de 0.5s)
        self.assertAlmostEqual(after.timestamp() -
                               before.timestamp(), 0.5, delta=0.5)

    # Teste que la méthode update ne modifie que les attributs existants
    def test_update_only_changes_existing_attributes(self):
        # Création d'une instance
        model = BaseModel()

        # Sauvegarde des valeurs originales
        original_id = model.id
        original_created = model.created_at
        previous_updated = model.updated_at

        # Appel de la méthode update avec un attribut inexistant
        model.update({
            'id': 'new-id-value',
            'created_at': original_created,
            'non_existing': 'should_be_ignored'
        })

        # Vérifie que l'id a été mis à jour
        self.assertEqual(model.id, 'new-id-value')

        # Vérifie que created_at est resté identique
        self.assertEqual(model.created_at, original_created)

        # Vérifie que l'attribut non_existing n’a pas été ajouté
        self.assertFalse(hasattr(model, 'non_existing'))

        # Vérifie que updated_at a bien été modifié
        self.assertGreater(model.updated_at, previous_updated)


# Point d'entrée pour exécuter les tests si le fichier est lancé directement
if __name__ == '__main__':
    unittest.main()
