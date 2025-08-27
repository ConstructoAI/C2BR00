# Fichier de redirection pour compatibilité avec Render
# Ce fichier existe pour résoudre un problème de configuration de déploiement

import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importer et lancer l'application principale
from app import *

if __name__ == "__main__":
    main()