% =====================================================================
% ResQ-Grid Knowledge Base: Emergency Unit Dispatch Rules
% Language: Prolog (Horn Clauses)
% =====================================================================

% --- FACTS: Unit Registry: unit(UnitId, VehicleType) ---
unit(a1, ambulance).
unit(a2, ambulance).
unit(f1, fire_truck).
unit(f2, fire_truck).
unit(b1, rescue_boat).

% --- FACTS: Resource Requirements: needs(IncidentKind, VehicleType) ---
needs(fire, fire_truck).
needs(flood, rescue_boat).
needs(medical, ambulance).

% --- FACTS: Active Incidents: incident(IncidentId, IncidentKind, Priority) ---
incident(inc_01, fire, high).
incident(inc_02, flood, high).
incident(inc_03, medical, medium).

% --- RULE: Deduction for Suitable Dispatch ---
% A unit U is suitable for incident I if unit U has type T,
% incident I is of kind K, and kind K needs vehicle type T.
suitable(U, I) :-
    unit(U, T),
    incident(I, K, _),
    needs(K, T).

% --- SAMPLE QUERIES ---
% ?- suitable(U, inc_01).  % Which units can handle fire incident inc_01?
% ?- suitable(U, I).       % All valid unit-to-incident allocations.
