<?php
/// ajoute des données à la base de données
$uploaddir = '/var/lib/photodb/db/';
$uploadfile = $uploaddir . basename($_FILES['userfile']['name']);

echo '<pre>';
$ok=copy($_FILES['userfile']['tmp_name'], $uploadfile);
if ($ok) {
    echo "Le fichier est valide, et a été téléchargé
           avec succès. Voici plus d'informations :\n";
} else {
    echo "Attaque potentielle par téléchargement de fichiers.
          Voici plus d'informations :\n";
}

echo "Voici quelques informations de débogage :\n\$uploadfile = ";
print_r($uploadfile);
echo "\n\$_FILES = ";
print_r($_FILES);

echo "</pre>\n";

if($ok){
    $cmd="cd /usr/share/photodb; ./csv2db.py db/".basename($_FILES['userfile']['name']);
    echo "$cmd<br/>\n";
    $lastline=system($cmd);
    echo "$lastline<br/>\n";
}

?>