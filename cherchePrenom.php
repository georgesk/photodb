<?php
header('Content-Type: application/json');
try{
    $pdo = new PDO('sqlite:'.dirname(__FILE__).'/db/names.db');
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION); // ERRMODE_WARNING | ERRMODE_EXCEPTION | ERRMODE_SILENT
} catch(Exception $e) {
    echo "Impossible d'accéder à la base de données SQLite : ".$e->getMessage();
    die();
}
$nom=$_GET["nom"];
$prenom=$_GET["prenom"];
$sth = $pdo->prepare("SELECT givenname
    FROM person
    WHERE surname = ?");
$data=[];
$sth->execute(array($nom));
foreach  ($sth->fetchAll() as $row) {
    array_push($data,$row["givenname"]);
}
echo json_encode($data);

?>
