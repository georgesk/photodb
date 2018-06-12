<?php
// envoi de données vers la base de données. les données sont dans $_POST
// les clés d'accès aux données sont "nom", "prenom", "photo".

include_once "commun.php";

header('Content-Type: application/json');
$nom=$_POST["nom"];
$prenom=$_POST["prenom"];
$photo=$_POST["photo"];
$data=[];

// vérification que la photo n'est pas déjà présente

$sth=$pdo->prepare ("SELECT photo FROM person where surname = ? and givenname = ?");
$result = $sth->execute(array($nom,$prenom));
$row=$sth->fetch();
// s'il y a zéro lignes, il faut traiter le cas de non/prénom inexistants
if (! $row){
    $data["statut"]="nouveau";
    echo json_encode($data);
    return;
}
// il y a au moins une ligne c'est sûr
if ($row["photo"]){
    // il y a déjà une photo
    $data["statut"]="dejavu";
    
    $data["photo"]=$row["photo"];
    $type = pathinfo($data["photo"], PATHINFO_EXTENSION);
    $photodata = file_get_contents($data["photo"]);
    $data["base64"] = 'data:image/' . $type . ';base64,' . base64_encode($photodata);
    
} else {
    // il n'y a pas de photo, on en enregistre une
    $nomfichier=nommage($nom, $prenom, $data);
    $pattern='@^data:image/jpeg;base64,(.*)@';
    preg_match($pattern, $photo, $matches);
    $base64=$matches[1];
    $decoded = base64_decode($base64);
    file_put_contents($nomfichier, $decoded);
    // refait le format d'image qui est fort bizarre
    $cmd="convert -resize 170x220\\! ".$nomfichier." ".$nomfichier.".tmp && mv ".$nomfichier.".tmp ".$nomfichier;
    system($cmd);
    date_default_timezone_set('UTC');
    $date=date('Y-m-d H:i:s');
    $sth=$pdo->prepare( 'UPDATE person SET photo=?, date=? WHERE surname=? and givenname=?' );
    $result = $sth->execute(Array($nomfichier,$nom,$prenom,$date));
    // on renvoie les données du fichier photo comme feedback
    $photodata = file_get_contents($nomfichier);
    $data["base64"] = 'data:image/jpeg;base64,' . base64_encode($photodata);
    
    $data["statut"]="ok";
}

echo json_encode($data);

?>
