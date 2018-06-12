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

// vérification que la photo n'est pas déjà présente

$sth=$pdo->prepare ("SELECT photo FROM person where surname = ? and givenname = ?");
$result = $sth->execute(array($nom,$prenom));
$row=$sth->fetch();
if ($row && $row["photo"]){
    // il y a déjà une photo, on l'efface du système de fichier
    unlink($row["photo"]);
    // on en enregistre la nouvelle photo
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
    date_default_timezone_set('UTC');
    $date=date('Y-m-d H:i:s');
    $sth = $pdo->prepare(" UPDATE person SET photo=?, date=? WHERE surname=? AND givenname=?");
    $result=$sth->execute(Array($nomfichier,$nom,$prenom,$date));
    $data["result"]=$result;
    // on renvoie les données du fichier photo comme feedback
    $photodata = file_get_contents($nomfichier);
    $data["base64"] = 'data:image/jpeg;base64,' . base64_encode($photodata);
    
    $data["statut"]="ok";
}

echo json_encode($data);

?>
