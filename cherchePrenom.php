<?php
include_once("commun.php");

header('Content-Type: application/json');

$nom=$_GET["nom"];
$prenom=$_GET["prenom"];
$sth = $pdo->prepare("SELECT givenname
    FROM person
    WHERE surname = ? and givenname LIKE ?");
$data=[];
$sth->execute(array($nom,"%".$prenom."%"));
foreach  ($sth->fetchAll() as $row) {
    array_push($data,$row["givenname"]);
}
echo json_encode($data);

?>
