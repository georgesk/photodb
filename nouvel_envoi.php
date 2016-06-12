<?php
// envoi de données vers la base de données. les données sont dans $_POST
// les clés d'accès aux données sont "nom", "prenom", "photo".
// l'utilisateur a déjà approuvé l'écrasement d'un fichier existant au
// préalable

include_once "commun.php";

header('Content-Type: application/json');
$nom=$_POST["nom"];
$prenom=$_POST["prenom"];
$photo=$_POST["photo"];
$data=[];

$db = new SQLite3('db/names.db');
// on enregistre la photo dans le système de fichiers
$nomfichier=nommage($nom, $prenom, $data);
$pattern='@^data:image/jpeg;base64,(.*)@';
preg_match($pattern, $photo, $matches);
$base64=$matches[1];
$decoded = base64_decode($base64);
file_put_contents($nomfichier, $decoded);
// refait le format d'image qui est fort bizarre
$cmd="convert -resize 170x220\\! ".$nomfichier." ".$nomfichier.".tmp && mv ".$nomfichier.".tmp ".$nomfichier;
system($cmd);
// on insère un nouvel enregistrement dans la base de données
$query="INSERT INTO person (surname, givenname, photo) VALUES ('".$nom."','".$prenom."','".$nomfichier."')";
$data["query"]=$query;
$result=$db->exec($query);
$data["result"]=$result;
// on renvoie les données du fichier photo comme feedback
$photodata = file_get_contents($nomfichier);
$data["base64"] = 'data:image/jpeg;base64,' . base64_encode($photodata);
    
$data["statut"]="ok";

echo json_encode($data);

?>
