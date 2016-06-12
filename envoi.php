<?php
// envoi de données vers la base de données. les données sont dans $_POST
header('Content-Type: application/json');
$db = new SQLite3('names.db');
echo json_encode($data);

?>
