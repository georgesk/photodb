<?php
// fonctions communes à plusieurs fichiers

/**
 * Renvoie à coup sûr une chaîne de caractères utilisable pour un nom de fichier
 * @param s une chaîne à protéger
 * @return un résultat sûr
 **/
function protege($s){
    return preg_replace('/[^A-Za-z0-9_\-]/', '_', $s);
}
/**
 * Renvoie à coup sûr une chaîne de caractères utilisable pour une requête SQL
 * @param s une chaîne à protéger
 * @return un résultat sûr
 **/
function protegeSQL($s){
    return str_replace("'","''");
}

/**
 * fonction utilisée pour créer les noms de fichiers
 * @param nom le nom et ...
 * @param prenom le prénom ... peuvent être utilisés dans le nom de fichier
 * @param data un tableau associatif ; on modifie $data["fichier"]
 * @return le nom de fichier obtenu
 **/
function nommage($nom, $prenom, $data){
    $nomfichier=substr(protege($nom."_".$prenom),0,20)."_";
    $nomfichier=uniqid("photos/".$nomfichier).".jpg";
    $data["fichier"]=$nomfichier;
    return $nomfichier;
}

?>