# -*- coding: utf-8 -*-

#####
# Vincent Latourelle (18 219 818)
# Charles Lachance (17 093 137)
# Manina Meng (21 161 779)
###

import numpy as np
import random
from sklearn import linear_model


class Regression:
    def __init__(self, lamb, m=1):
        self.lamb = lamb
        self.w = None
        self.M = m

    def fonction_base_polynomiale(self, x):
        """
        Fonction de base qui projette la donnee x vers un espace polynomial tel que mentionne au chapitre 3.
        Si x est un scalaire, alors phi_x sera un vecteur à self.M dimensions : (x^1,x^2,...,x^self.M)
        Si x est un vecteur de N scalaires, alors phi_x sera un tableau 2D de taille NxM

        NOTE : En mettant phi_x = x, on a une fonction de base lineaire qui fonctionne pour une regression lineaire
        """
        # Retourne phi_x
        # Si c'est un scalaire : [x^0, x^1, ... x^M-1]
        # Si c'est un vecteur : [[x0^0,x1^0,...xM-1^0],....,[x0^M-1,x1^M-1,...xM-1^M-1]]T
        return np.transpose([np.power(x,j) for j in range(0, self.M)])
        

    def recherche_hyperparametre(self, X, t):
        """
        Validation croisee de type "k-fold" pour k=10 utilisee pour trouver la meilleure valeur pour
        l'hyper-parametre self.M.

        Le resultat est mis dans la variable self.M

        X: vecteur de donnees
        t: vecteur de cibles
        """
        k = 10
        resultat = {}
        # Pour chaque valeur d'hyperparametre M possible entre 1 et 20
        for m in range(1, 20):
            erreur_validation_moyenne = 0
            self.M = m
            for j in range(0, k):
                # Determiner un separateur aleatoirement et separer les donnees d'entrainement en 2 zones
                separateur = random.randint(1, len(X)-1)
                X_train = X[:separateur]
                X_valid = X[separateur:]
                t_train = t[:separateur]
                t_valid = t[separateur:]

                # Entrainner sur une partie des donnees et valider sur l'autre
                self.entrainement(X_train, t_train)

                predictions_validation = np.array([self.prediction(x) for x in X_valid])

                # Calculer l'erreur de validation et l'additionner au total pour l'erreur de validation pour un m donne
                erreur_validation = np.array([self.erreur(t_n, p_n)
                                     for t_n, p_n in zip(t_valid, predictions_validation)])
                erreur_validation_moyenne += erreur_validation.mean()
            
            #Calcule la moyenne des erreurs de validation pour ce m
            resultat[m] = erreur_validation_moyenne / k

        # https://stackoverflow.com/questions/3282823/get-the-key-corresponding-to-the-minimum-value-within-a-dictionary
        # Obtient la cle ayant la valeur minimum dans le dictionnaire
        self.M  = min(resultat, key=resultat.get)

    def entrainement(self, X, t, using_sklearn=False):
        """
        Entraîne la regression lineaire sur l'ensemble d'entraînement forme des
        entrees ``X`` (un tableau 2D Numpy, ou la n-ieme rangee correspond à l'entree
        x_n) et des cibles ``t`` (un tableau 1D Numpy ou le
        n-ieme element correspond à la cible t_n). L'entraînement doit
        utiliser le poids de regularisation specifie par ``self.lamb``.

        Cette methode doit assigner le champs ``self.w`` au vecteur
        (tableau Numpy 1D) de taille D+1, tel que specifie à la section 3.1.4
        du livre de Bishop.
        
        Lorsque using_sklearn=True, vous devez utiliser la classe "Ridge" de 
        la librairie sklearn (voir http://scikit-learn.org/stable/modules/linear_model.html)
        
        Lorsque using_sklearn=Fasle, vous devez implementer l'equation 3.28 du
        livre de Bishop. Il est suggere que le calcul de ``self.w`` n'utilise
        pas d'inversion de matrice, mais utilise plutôt une procedure
        de resolution de systeme d'equations lineaires (voir np.linalg.solve).

        Aussi, la variable membre self.M sert à projeter les variables X vers un espace polynomiale de degre M
        (voir fonction self.fonction_base_polynomiale())

        NOTE IMPORTANTE : lorsque self.M <= 0, il faut trouver la bonne valeur de self.M

        """
        if self.M <= 0:
            self.recherche_hyperparametre(X, t)

        phi_x = self.fonction_base_polynomiale(X)

        if using_sklearn == True :
            reg = linear_model.Ridge(alpha=self.lamb)
            reg.fit(phi_x, t)
            self.w = reg.coef_
            self.w[0] = reg.intercept_

        elif using_sklearn == False :
            a = np.matmul(np.transpose(phi_x),phi_x) + self.lamb * np.identity(self.M)
            b = np.matmul(np.transpose(phi_x), t)
            self.w = np.linalg.solve(a, b)

    def prediction(self, x):
        """
        Retourne la prediction de la regression lineaire
        pour une entree, representee par un tableau 1D Numpy ``x``.

        Cette methode suppose que la methode ``entrainement()``
        a prealablement ete appelee. Elle doit utiliser le champs ``self.w``
        afin de calculer la prediction y(x,w) (equation 3.1 et 3.3).
        """
        phi_x = self.fonction_base_polynomiale(x)
        return np.dot(self.w, phi_x)

    @staticmethod
    def erreur(t, prediction):
        """
        Retourne l'erreur de la difference au carre entre
        la cible ``t`` et la prediction ``prediction``.
        """
        return np.power(t-prediction, 2)
