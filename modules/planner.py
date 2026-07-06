# ============================================================
# MODULE 7: AI Planning — Treatment Plan Generator
# Covers: Week 12 (AI Planning Techniques)
# ============================================================

from copy import deepcopy
from collections import deque
from typing import Dict, List, Set, Tuple, Optional

class TreatmentPlanner:
    """
    STRIPS-based treatment planner.
    Generates step-by-step treatment plans
    from patient diagnosis to recovery.
    """

    def __init__(self):
        self.action_library = self._build_action_library()

    def _build_action_library(self) -> List[Dict]:
        """Define medical treatment actions"""
        return [
            # Emergency Actions
            {
                'name': 'CallEmergencyServices',
                'precond': {'EMERGENCY_CASE', 'PATIENT_PRESENT'},
                'delete':  {'EMERGENCY_CASE'},
                'add':     {'EMERGENCY_SERVICES_CALLED'},
                'cost': 0, 'duration': '5 minutes'
            },
            {
                'name': 'TransferToICU',
                'precond': {'EMERGENCY_SERVICES_CALLED', 'ICU_AVAILABLE'},
                'delete':  {'EMERGENCY_SERVICES_CALLED'},
                'add':     {'PATIENT_IN_ICU', 'MONITORING_ACTIVE'},
                'cost': 0, 'duration': '15 minutes'
            },
            # Diagnostics
            {
                'name': 'OrderBloodPanel',
                'precond': {'PATIENT_PRESENT', 'DIAGNOSIS_NEEDED'},
                'delete':  {'DIAGNOSIS_NEEDED'},
                'add':     {'BLOOD_RESULTS_PENDING'},
                'cost': 1, 'duration': '30 minutes'
            },
            {
                'name': 'ReceiveBloodResults',
                'precond': {'BLOOD_RESULTS_PENDING'},
                'delete':  {'BLOOD_RESULTS_PENDING'},
                'add':     {'BLOOD_RESULTS_AVAILABLE', 'DIAGNOSIS_REFINED'},
                'cost': 0, 'duration': '2 hours'
            },
            {
                'name': 'OrderPCRTest',
                'precond': {'COVID_SUSPECTED', 'PATIENT_PRESENT'},
                'delete':  {'COVID_SUSPECTED'},
                'add':     {'PCR_PENDING'},
                'cost': 1, 'duration': '24 hours'
            },
            {
                'name': 'ReceivePCRResult',
                'precond': {'PCR_PENDING'},
                'delete':  {'PCR_PENDING'},
                'add':     {'PCR_RESULT_AVAILABLE', 'DIAGNOSIS_CONFIRMED'},
                'cost': 0, 'duration': '24 hours'
            },
            # Treatment
            {
                'name': 'PrescribeAntiviral',
                'precond': {'DIAGNOSIS_CONFIRMED', 'VIRAL_INFECTION'},
                'delete':  {'VIRAL_INFECTION'},
                'add':     {'ANTIVIRAL_PRESCRIBED', 'TREATMENT_STARTED'},
                'cost': 1, 'duration': '10 minutes'
            },
            {
                'name': 'PrescribeAntibiotics',
                'precond': {'DIAGNOSIS_CONFIRMED', 'BACTERIAL_INFECTION'},
                'delete':  {'BACTERIAL_INFECTION'},
                'add':     {'ANTIBIOTICS_PRESCRIBED', 'TREATMENT_STARTED'},
                'cost': 1, 'duration': '10 minutes'
            },
            {
                'name': 'AdministerFluids',
                'precond': {'PATIENT_IN_ICU', 'DEHYDRATION_RISK'},
                'delete':  {'DEHYDRATION_RISK'},
                'add':     {'FLUIDS_ADMINISTERED'},
                'cost': 1, 'duration': '1 hour'
            },
            {
                'name': 'MonitorVitals',
                'precond': {'TREATMENT_STARTED', 'PATIENT_PRESENT'},
                'delete':  set(),
                'add':     {'VITALS_MONITORED'},
                'cost': 0, 'duration': 'Continuous'
            },
            {
                'name': 'IsolatePatient',
                'precond': {'CONTAGIOUS_DISEASE', 'PATIENT_PRESENT'},
                'delete':  {'CONTAGIOUS_DISEASE'},
                'add':     {'PATIENT_ISOLATED'},
                'cost': 0, 'duration': '14 days'
            },
            {
                'name': 'ScheduleFollowUp',
                'precond': {'TREATMENT_STARTED', 'VITALS_MONITORED'},
                'delete':  set(),
                'add':     {'FOLLOWUP_SCHEDULED', 'PLAN_COMPLETE'},
                'cost': 0, 'duration': '5 minutes'
            },
            {
                'name': 'DischargePatient',
                'precond': {'PLAN_COMPLETE', 'SYMPTOMS_RESOLVED'},
                'delete':  {'PLAN_COMPLETE'},
                'add':     {'PATIENT_DISCHARGED'},
                'cost': 0, 'duration': '30 minutes'
            },
            # FIX: the original action library had no way for ANY
            # non-COVID diagnosis to ever reach DIAGNOSIS_CONFIRMED
            # (only the PCR pipeline produced it, and that's gated on
            # COVID_SUSPECTED). This generic lab-confirmation action
            # gives every other disease a route to a confirmed
            # diagnosis via the blood panel. It is gated on
            # NON_COVID_CASE so it can never shortcut the intended
            # isolate -> PCR -> antiviral pipeline for COVID-19.
            {
                'name': 'ConfirmDiagnosisFromLabs',
                'precond': {'BLOOD_RESULTS_AVAILABLE', 'NON_COVID_CASE'},
                'delete':  set(),
                'add':     {'DIAGNOSIS_CONFIRMED'},
                'cost': 1, 'duration': '1 hour'
            },
            # FIX: diabetes has neither VIRAL_INFECTION nor
            # BACTERIAL_INFECTION, so it could never trigger any
            # existing "start treatment" action.
            {
                'name': 'PrescribeInsulin',
                'precond': {'DIAGNOSIS_CONFIRMED', 'METABOLIC_CONDITION'},
                'delete':  {'METABOLIC_CONDITION'},
                'add':     {'TREATMENT_STARTED'},
                'cost': 1, 'duration': '10 minutes'
            },
            # FIX: cardiac_event had no action at all that produces
            # TREATMENT_STARTED once the patient reaches the ICU.
            {
                'name': 'AdministerCardiacCare',
                'precond': {'PATIENT_IN_ICU'},
                'delete':  set(),
                'add':     {'TREATMENT_STARTED'},
                'cost': 1, 'duration': '20 minutes'
            },
        ]

    def _apply_action(self, state: frozenset,
                      action: Dict) -> Optional[frozenset]:
        if not action['precond'].issubset(state):
            return None
        return frozenset((state - action['delete']) | action['add'])

    def generate_plan(self,
                      initial_state: Set[str],
                      goal_state:    Set[str]) -> Optional[List[Dict]]:
        """BFS-based plan generation"""
        initial = frozenset(initial_state)
        goal    = frozenset(goal_state)

        queue   = deque([(initial, [])])
        visited = {initial}

        while queue:
            state, plan = queue.popleft()
            if goal.issubset(state):
                return plan

            for action in self.action_library:
                new_state = self._apply_action(state, action)
                if new_state and new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, plan + [action]))

        return None

    def create_treatment_plan(self, diagnosis: str,
                              urgency: str) -> Dict:
        """Generate a treatment plan for a given diagnosis"""

        # Map diagnosis to initial state predicates
        # FIX: covid19 is missing VIRAL_INFECTION (needed to ever fire
        # PrescribeAntiviral); every non-covid entry now carries
        # NON_COVID_CASE so it can use the generic lab-confirmation
        # route; diabetes carries METABOLIC_CONDITION so it can reach
        # treatment via PrescribeInsulin; meningitis is missing
        # DIAGNOSIS_NEEDED so it had no route to a confirmed diagnosis.
        diagnosis_states = {
            'flu':          {'VIRAL_INFECTION', 'DIAGNOSIS_NEEDED',
                             'NON_COVID_CASE'},
            'covid19':      {'COVID_SUSPECTED', 'CONTAGIOUS_DISEASE',
                             'DIAGNOSIS_NEEDED', 'VIRAL_INFECTION'},
            'cardiac_event':{'EMERGENCY_CASE',  'ICU_AVAILABLE',
                             'NON_COVID_CASE'},
            'dengue':       {'VIRAL_INFECTION',  'DIAGNOSIS_NEEDED',
                             'DEHYDRATION_RISK', 'NON_COVID_CASE'},
            'meningitis':   {'EMERGENCY_CASE',  'BACTERIAL_INFECTION',
                             'ICU_AVAILABLE', 'DIAGNOSIS_NEEDED',
                             'NON_COVID_CASE'},
            'tuberculosis': {'BACTERIAL_INFECTION', 'CONTAGIOUS_DISEASE',
                             'DIAGNOSIS_NEEDED', 'NON_COVID_CASE'},
            'diabetes':     {'DIAGNOSIS_NEEDED', 'METABOLIC_CONDITION',
                             'NON_COVID_CASE'},
            'common_cold':  {'VIRAL_INFECTION', 'DIAGNOSIS_NEEDED',
                             'NON_COVID_CASE'},
        }

        base_state = {'PATIENT_PRESENT'}
        dx_state   = diagnosis_states.get(
            diagnosis.lower().replace(' ', '_'),
            {'DIAGNOSIS_NEEDED', 'NON_COVID_CASE'}
        )
        initial_state = base_state | dx_state

        # Goal state: always end with treatment and monitoring
        goal_state = {'TREATMENT_STARTED', 'VITALS_MONITORED',
                      'FOLLOWUP_SCHEDULED'}
        if urgency == 'CRITICAL':
            goal_state.add('PATIENT_IN_ICU')
            # FIX: CRITICAL cases need an ICU route available even for
            # diagnoses that don't normally carry EMERGENCY_CASE.
            initial_state = initial_state | {'EMERGENCY_CASE', 'ICU_AVAILABLE'}
        # FIX: contagious diseases must actually require isolation as
        # part of the goal -- otherwise BFS (shortest-plan search) will
        # always skip it, since it wasn't contributing to reaching the
        # goal state at all.
        if 'CONTAGIOUS_DISEASE' in initial_state:
            goal_state.add('PATIENT_ISOLATED')

        plan = self.generate_plan(initial_state, goal_state)

        if plan is None:
            return {'error': 'No plan found', 'plan': []}

        return {
            'diagnosis':     diagnosis,
            'urgency':       urgency,
            'initial_state': sorted(initial_state),
            'goal_state':    sorted(goal_state),
            'steps':         len(plan),
            'total_duration': self._estimate_duration(plan),
            'plan': [
                {
                    'step':     i+1,
                    'action':   a['name'],
                    'duration': a['duration'],
                    'cost':     a['cost']
                }
                for i, a in enumerate(plan)
            ]
        }

    def _estimate_duration(self, plan: List[Dict]) -> str:
        durations = [a['duration'] for a in plan]
        return f"{len(plan)} actions | see individual durations"

    def analyze(self, percept) -> Dict:
        """Module interface — generates a sample plan"""
        # This is called post-diagnosis; use KB result
        result = self.create_treatment_plan('flu', 'MEDIUM')
        result['summary']    = f"Plan: {result['steps']} steps generated"
        result['diagnosis']  = 'flu'
        result['confidence'] = 0.7
        return result
