<?php
// envoi de données vers la base de données. les données sont dans $_POST
// les clés d'accès aux données sont "nom", "prenom", "photo".
// l'utilisateur a déjà approuvé l'écrasement d'un fichier existant au
// préalable
header('Content-Type: application/json');
$nom=$_POST["nom"];
$prenom=$_POST["prenom"];
$photo=$_POST["photo"];
$data=[];

$db = new SQLite3('db/names.db');
// on enregistre la photo dans le système de fichiers
$nomFichier=substr($nom,0,3)."_";
$nomfichier=uniqid("photos/".$nomFichier).".jpg";
$data["fichier"]=$nomfichier;
$pattern='@^data:image/jpeg;base64,(.*)@';
preg_match($pattern, $photo, $matches);
$base64=$matches[1];
$decoded = base64_decode($base64);
file_put_contents($nomfichier, $decoded);
// refait le format d'image qui est fort bizarre
$cmd="convert -resize 170x220\\! ".$nomfichier." ".$nomfichier.".tmp && mv ".$nomfichier.".tmp ".$nomfichier;
system($cmd);
// on insère un nouvel enregistrement dans la base de données    
$stm=$db->prepare( 'INSERT INTO person (surname, givenname, photo) VALUES (:surname,:givenname,:photo)');
$stm->bindValue(':photo', $nomfichier, SQLITE3_TEXT);
$stm->bindValue(':nom', $nom, SQLITE3_TEXT);
$stm->bindValue(':prenom', $prenom, SQLITE3_TEXT);
$result = $stm->execute();
// on renvoie les données du fichier photo comme feedback
$photodata = file_get_contents($nomfichier);
$data["base64"] = 'data:image/jpeg;base64,' . base64_encode($photodata);
    
$data["statut"]="ok";
}

echo json_encode($data);

?>
