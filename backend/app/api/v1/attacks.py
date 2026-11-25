from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.attack import AttackScenario, SimulationRun
from backend.app.schemas.attack import AttackScenarioRead, SimulationRunCreate, SimulationRunRead
from backend.app.schemas.common import ResponseEnvelope
from backend.app.services.attack_engine.registry import AttackRegistry
from backend.app.services.attack_engine.runner import AttackRunner
import backend.app.services.attack_engine.scenarios  # ensure loaded

router = APIRouter(prefix="/attacks", tags=["Attack Simulator"])

@router.get("", response_model=ResponseEnvelope[List[AttackScenarioRead]])
def list_scenarios(
    category: Optional[str] = Query(None, description="Filter by attack category"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    db: Session = Depends(get_db)
):
    """List all available attack scenarios in the catalog."""
    query = db.query(AttackScenario).filter(AttackScenario.is_active == True)
    if category:
        query = query.filter(AttackScenario.category.ilike(f"%{category}%"))
    if severity:
        query = query.filter(AttackScenario.severity.ilike(severity))
    scenarios = query.order_by(AttackScenario.id).all()
    return ResponseEnvelope(data=scenarios)

@router.get("/scenarios/{scenario_id}", response_model=ResponseEnvelope[AttackScenarioRead])
def get_scenario(scenario_id: str, db: Session = Depends(get_db)):
    """Retrieve full details of an attack scenario."""
    scenario = db.query(AttackScenario).filter(AttackScenario.id == scenario_id).first()
    if not scenario:
        raise HTTPException(status_code=404, detail="Attack scenario not found")
    return ResponseEnvelope(data=scenario)

@router.post("/simulate", response_model=ResponseEnvelope[SimulationRunRead])
def simulate_attack(
    payload: SimulationRunCreate,
    db: Session = Depends(get_db)
):
    """Execute a simulated attack scenario against an assessment target."""
    try:
        run = AttackRunner.run_simulation(
            db=db,
            assessment_id=payload.assessment_id,
            scenario_id=payload.scenario_id,
            mode=payload.mode,
            custom_input=payload.custom_input
        )
        return ResponseEnvelope(
            data=run,
            message=f"Simulation '{payload.scenario_id}' executed ({run.status})."
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/batch-simulate/{assessment_id}", response_model=ResponseEnvelope[List[SimulationRunRead]])
def batch_simulate(
    assessment_id: str,
    mode: str = Query("vulnerable", description="Execution mode: vulnerable or protected"),
    db: Session = Depends(get_db)
):
    """Execute all 14 attack scenarios against an assessment."""
    try:
        runs = AttackRunner.run_all_scenarios(
            db=db,
            assessment_id=assessment_id,
            mode=mode
        )
        return ResponseEnvelope(
            data=runs,
            message=f"Batch simulation completed: {len(runs)} scenarios evaluated in {mode} mode."
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/runs", response_model=ResponseEnvelope[List[SimulationRunRead]])
def list_simulation_runs(
    assessment_id: Optional[str] = Query(None),
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List recorded simulation runs."""
    query = db.query(SimulationRun)
    if assessment_id:
        query = query.filter(SimulationRun.assessment_id == assessment_id)
    runs = query.order_by(SimulationRun.created_at.desc()).limit(limit).all()
    return ResponseEnvelope(data=runs)

@router.get("/runs/{run_id}", response_model=ResponseEnvelope[SimulationRunRead])
def get_simulation_run(run_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed evidence and invariant results for a specific simulation run."""
    run = db.query(SimulationRun).filter(SimulationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Simulation run not found")
    return ResponseEnvelope(data=run)

