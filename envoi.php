<?php
// envoi de données vers la base de données. les données sont dans $_POST
// les clés d'accès aux données sont "nom", "prenom", "photo".
header('Content-Type: application/json');
$db = new SQLite3('names.db');
$nom=$_POST["nom"];
$prenom=$_POST["prenom"];
$photo=$_POST["photo"];
$data=[];
// vérification que la photo n'est pas déjà présente
$result = $db->query("SELECT photo FROM person where surname = '".$nom."' and givenname = '".$prenom."'");
if ($result->numRows()>0){
    // il y a déjà une photo
    $data["statut"]="dejavu";
    $data["photo"]=sqlite_fetch_single($result);
    $type = pathinfo($data["photo"], PATHINFO_EXTENSION);
    $photodata = file_get_contents($data["photo"]);
    $data["base64"] = 'data:image/' . $type . ';base64,' . base64_encode($photodata);
} else {
    // il n'y a pas de photo, on en enregistre une
    $nomFichier=substr($nom,0,3)."_";
    $nomfichier=uniqid("photos/".$nomFichier).".jpg";
    $decoded = base64_decode(substr($photo,22));
    file_put_contents($nomfichier, $decoded);
    $data["statut"]="ok";
}

echo json_encode($data);

?>
