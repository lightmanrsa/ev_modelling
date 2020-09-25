..  VencoPy introduction file created on February 11, 2020
    by Niklas Wulff
    Licensed under CC BY 4.0: https://creativecommons.org/licenses/by/4.0/deed.en
    
.. _intro:

Introduction
===================================


Future electric vehicle fleets pose both challenges and opportunities for power systems. While increased power demand from transport electrification necessitates expansion of power supply, vehicle batteries can to a certain degree shift their charging load to times of high availability of power. The model-adequate description of power demand from future plug-in electric vehicle fleets is a pre-requisite for modelling sector-coupled energy systems and drawing respective policy-relevant conclusions. Vehicle Energy Consumption in Python (VencoPy) is a tool that provides boundary conditions for load shifting and vehicle-to-grid potentials based on transport demand data and techno-economic assumptions. 

.. image:: VencoPy_Schema.png
   :width: 600

Structurally, VencoPy follows five phases that are shown in the above schema:

1.  Input read-in and cleaning
2.  Calculation of the six VencoPy profiles on an individual profile level
3.  Filtering of profiles
4.  Aggregation of profiles to a fleet level
5.  Output and plotting

In its current version, step 1 draws from the libraries :file:`libInput.py` and pre-processing, steps 2-4 draw from the library :file:`libProfileCalculation.py` and output draws from :file:`libOutput.py`. 

VencoPy has so far been applied to the German travel survey (Mobilität in Deutschland) on a national scale to derive hourly load-shifting constraining profiles for the energy system optimization model REMix.


Zukünftige Flotten elektrisch angetriebener Fahrzeuge sind sowohl Chancen als auch Risiken für Energiesysteme. Auf der einen Seite erfordert eine Elektrifizierung des Verkehrs einen ausgeweiteten Kraftwerkspark, auf der anderen Seite können Batterien in gewissen Grenzen eine Flexibilitätsoption für das Stromsystem darstellen. Die angemessene Beschreibung der Stromnachfrage zukünftiger elektrischer Plug-in-Fahrzeugflotten ist eine Voraussetzung für die Modellierung sektorgekoppelter Energiesysteme und die Bereitstellung politikrelevanter Erkenntnisse. Vehicle Energy Consumption in Python (VencoPy) ist ein Tool, das Randbedingungen für das Ladeverhalten und möglicher Vehicle-to-Grid Potenziale basierend auf Mobilitätsdaten und techno-ökonomischen Annahmen berechnet. 

.. image:: VencoPy_SchemaDE.png
   :width: 600

Strukturell folgt VencoPy fünf Phasen, die in der Abbildung dargestellt sind: 

1.  Input einlesen und verarbeiten
2.  Berechnung der sechs geschätzten Flexibilitätsprofile auf der Ebene der Einzelprofile
3.  Filtern der Profile
4.  Aggregation der Einzelprofile auf Flottenebene
5.  Output und Darstellung

Aktuell basiert Schritt 1 auf der Bibliothek :file:`libInput.py` and :file:`libPreprocessing`, Schritte 2-4 nutzen Funktionen aus :file:`libProfileCalculation.py` und Ergebnisse werden mithilfe von Funktionen aus :file:`libOutput.py` geschrieben. 

VencoPy wurde bisher auf die deutsche Verkehrserhebung "Mobilität in Deutschland" angewendet, um den Einfluss des Nutzerverhaltens auf das zukünftige Lastverschiebepotenzial und dessen Auswirkungen auf das deutsche Stromsystem zu untersuchen. 