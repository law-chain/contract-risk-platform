"""
End-to-end API integration test.

Scenario: "Acme Corp" (buyer) contracts "CloudHost Ltd" (supplier)
for managed cloud infrastructure hosting at $500,000/year.

We walk through the entire workflow:
  1. Create engagement
  2. Add parties (buyer + supplier)
  3. Add goods/service (Cloud Hosting)
  4. Add failure modes (service outage + data breach)
  5. Add loss scenarios per failure mode
  6. Add mitigations and link to failure modes
  7. Run Monte Carlo quantification
  8. Verify dashboard results
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# In-memory SQLite for test isolation — StaticPool ensures all connections
# share the same in-memory database (otherwise each connection gets its own)
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def create_engagement():
    r = client.post("/api/engagements", json={
        "name": "Acme Corp — Cloud Hosting Contract",
        "description": "Managed cloud infrastructure for production workloads",
        "contract_value": 500_000,
        "currency": "USD",
        "industry": "Technology",
        "status": "draft",
    })
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["name"] == "Acme Corp — Cloud Hosting Contract"
    assert data["contract_value"] == 500_000
    return data


def add_parties(eid: int):
    buyer = client.post(f"/api/engagements/{eid}/parties", json={
        "name": "Acme Corp",
        "role": "buyer",
        "revenue": 10_000_000,
        "criticality": "high",
        "description": "Primary buyer — depends on cloud hosting for all production systems",
    })
    assert buyer.status_code == 201, buyer.text

    supplier = client.post(f"/api/engagements/{eid}/parties", json={
        "name": "CloudHost Ltd",
        "role": "supplier",
        "revenue": 50_000_000,
        "criticality": "medium",
        "description": "Cloud infrastructure provider",
    })
    assert supplier.status_code == 201, supplier.text
    return buyer.json(), supplier.json()


def add_goods_service(eid: int):
    r = client.post(f"/api/engagements/{eid}/goods-services", json={
        "name": "Managed Cloud Infrastructure",
        "category": "IT Services",
        "description": "Production cloud hosting including compute, storage, and networking",
        "use_context": "Runs all customer-facing web applications and APIs",
        "supply_type": "services",
        "replaceability": "difficult",
    })
    assert r.status_code == 201, r.text
    return r.json()


def add_failure_modes(eid: int, gs_id: int):
    # Failure mode 1: Service outage (relatively frequent, moderate severity)
    fm1 = client.post(f"/api/engagements/{eid}/failure-modes", json={
        "goods_service_id": gs_id,
        "name": "Cloud Service Outage",
        "description": "Unplanned downtime affecting production workloads",
        "category": "Availability",
        "frequency_low": 1.0,
        "frequency_mid": 3.0,
        "frequency_high": 6.0,
        "detection": "high",
        "source": "manual",
        "is_included": True,
    })
    assert fm1.status_code == 201, fm1.text

    # Failure mode 2: Data breach (rare but severe)
    fm2 = client.post(f"/api/engagements/{eid}/failure-modes", json={
        "goods_service_id": gs_id,
        "name": "Data Breach via Provider",
        "description": "Unauthorized access to customer data due to provider security failure",
        "category": "Security",
        "frequency_low": 0.01,
        "frequency_mid": 0.05,
        "frequency_high": 0.2,
        "detection": "low",
        "source": "manual",
        "is_included": True,
    })
    assert fm2.status_code == 201, fm2.text

    return fm1.json(), fm2.json()


def add_loss_scenarios(eid: int, fm1_id: int, fm2_id: int, buyer_id: int, supplier_id: int):
    # Outage → buyer loses revenue
    ls1 = client.post(f"/api/engagements/{eid}/failure-modes/{fm1_id}/loss-scenarios", json={
        "affected_party_id": buyer_id,
        "name": "Revenue loss from downtime",
        "loss_category": "revenue_loss",
        "severity_low": 5_000,
        "severity_mid": 25_000,
        "severity_high": 100_000,
        "distribution_type": "lognormal",
    })
    assert ls1.status_code == 201, ls1.text

    # Outage → buyer incurs recovery costs
    ls2 = client.post(f"/api/engagements/{eid}/failure-modes/{fm1_id}/loss-scenarios", json={
        "affected_party_id": buyer_id,
        "name": "Incident recovery costs",
        "loss_category": "direct",
        "severity_low": 2_000,
        "severity_mid": 8_000,
        "severity_high": 30_000,
        "distribution_type": "triangular",
    })
    assert ls2.status_code == 201, ls2.text

    # Data breach → buyer: regulatory fines + customer compensation
    ls3 = client.post(f"/api/engagements/{eid}/failure-modes/{fm2_id}/loss-scenarios", json={
        "affected_party_id": buyer_id,
        "name": "Regulatory fines and customer compensation",
        "loss_category": "regulatory",
        "severity_low": 50_000,
        "severity_mid": 500_000,
        "severity_high": 5_000_000,
        "distribution_type": "lognormal",
    })
    assert ls3.status_code == 201, ls3.text

    # Data breach → supplier: reputational damage
    ls4 = client.post(f"/api/engagements/{eid}/failure-modes/{fm2_id}/loss-scenarios", json={
        "affected_party_id": supplier_id,
        "name": "Supplier reputational damage",
        "loss_category": "reputational",
        "severity_low": 10_000,
        "severity_mid": 100_000,
        "severity_high": 1_000_000,
        "distribution_type": "lognormal",
    })
    assert ls4.status_code == 201, ls4.text

    return ls1.json(), ls2.json(), ls3.json(), ls4.json()


def add_mitigations(eid: int, fm1_id: int, fm2_id: int):
    # Mitigation 1: Multi-region failover (reduces outage frequency & severity)
    mit1 = client.post(f"/api/engagements/{eid}/mitigations", json={
        "name": "Multi-region failover",
        "description": "Deploy across multiple cloud regions with automatic failover",
        "mitigation_type": "operational",
        "cost": 60_000,
    })
    assert mit1.status_code == 201, mit1.text
    mit1_id = mit1.json()["id"]

    # Link to outage failure mode
    link1 = client.post(f"/api/engagements/{eid}/mitigations/{mit1_id}/link", json={
        "failure_mode_id": fm1_id,
        "frequency_reduction": 0.5,
        "severity_reduction": 0.4,
    })
    assert link1.status_code == 201, link1.text

    # Mitigation 2: Enhanced security audit (reduces breach frequency)
    mit2 = client.post(f"/api/engagements/{eid}/mitigations", json={
        "name": "Annual security audit & pen testing",
        "description": "Regular third-party security audits of provider infrastructure",
        "mitigation_type": "contractual",
        "cost": 25_000,
    })
    assert mit2.status_code == 201, mit2.text
    mit2_id = mit2.json()["id"]

    # Link to data breach failure mode
    link2 = client.post(f"/api/engagements/{eid}/mitigations/{mit2_id}/link", json={
        "failure_mode_id": fm2_id,
        "frequency_reduction": 0.6,
        "severity_reduction": 0.2,
    })
    assert link2.status_code == 201, link2.text

    return mit1.json(), mit2.json()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestHealthCheck:
    def test_health(self):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


class TestEngagementCRUD:
    def test_create_and_get(self):
        eng = create_engagement()
        eid = eng["id"]

        r = client.get(f"/api/engagements/{eid}")
        assert r.status_code == 200
        assert r.json()["name"] == eng["name"]

    def test_list(self):
        create_engagement()
        r = client.get("/api/engagements")
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_update(self):
        eng = create_engagement()
        eid = eng["id"]
        r = client.put(f"/api/engagements/{eid}", json={"name": "Updated Name"})
        assert r.status_code == 200
        assert r.json()["name"] == "Updated Name"

    def test_delete(self):
        eng = create_engagement()
        eid = eng["id"]
        r = client.delete(f"/api/engagements/{eid}")
        assert r.status_code == 204


class TestPartiesCRUD:
    def test_add_and_list(self):
        eng = create_engagement()
        buyer, supplier = add_parties(eng["id"])
        assert buyer["role"] == "buyer"
        assert supplier["role"] == "supplier"

        r = client.get(f"/api/engagements/{eng['id']}/parties")
        assert r.status_code == 200
        assert len(r.json()) == 2


class TestGoodsServicesCRUD:
    def test_add_and_list(self):
        eng = create_engagement()
        gs = add_goods_service(eng["id"])
        assert gs["name"] == "Managed Cloud Infrastructure"
        assert gs["replaceability"] == "difficult"

        r = client.get(f"/api/engagements/{eng['id']}/goods-services")
        assert r.status_code == 200
        assert len(r.json()) == 1


class TestFailureModesCRUD:
    def test_add_and_list(self):
        eng = create_engagement()
        gs = add_goods_service(eng["id"])
        fm1, fm2 = add_failure_modes(eng["id"], gs["id"])
        assert fm1["name"] == "Cloud Service Outage"
        assert fm2["category"] == "Security"

        r = client.get(f"/api/engagements/{eng['id']}/failure-modes")
        assert r.status_code == 200
        assert len(r.json()) == 2

    def test_toggle_include(self):
        eng = create_engagement()
        gs = add_goods_service(eng["id"])
        fm1, _ = add_failure_modes(eng["id"], gs["id"])
        assert fm1["is_included"] is True

        r = client.patch(f"/api/engagements/{eng['id']}/failure-modes/{fm1['id']}/toggle")
        assert r.status_code == 200
        assert r.json()["is_included"] is False

        r = client.patch(f"/api/engagements/{eng['id']}/failure-modes/{fm1['id']}/toggle")
        assert r.status_code == 200
        assert r.json()["is_included"] is True


class TestLossScenarios:
    def test_add_and_list(self):
        eng = create_engagement()
        buyer, supplier = add_parties(eng["id"])
        gs = add_goods_service(eng["id"])
        fm1, fm2 = add_failure_modes(eng["id"], gs["id"])
        scenarios = add_loss_scenarios(eng["id"], fm1["id"], fm2["id"], buyer["id"], supplier["id"])
        assert len(scenarios) == 4

        r = client.get(f"/api/engagements/{eng['id']}/failure-modes/{fm1['id']}/loss-scenarios")
        assert r.status_code == 200
        assert len(r.json()) == 2  # 2 scenarios for outage

        r = client.get(f"/api/engagements/{eng['id']}/failure-modes/{fm2['id']}/loss-scenarios")
        assert r.status_code == 200
        assert len(r.json()) == 2  # 2 scenarios for data breach


class TestMitigations:
    def test_add_and_link(self):
        eng = create_engagement()
        gs = add_goods_service(eng["id"])
        fm1, fm2 = add_failure_modes(eng["id"], gs["id"])
        mit1, mit2 = add_mitigations(eng["id"], fm1["id"], fm2["id"])
        assert mit1["cost"] == 60_000
        assert mit2["mitigation_type"] == "contractual"

        r = client.get(f"/api/engagements/{eng['id']}/mitigations")
        assert r.status_code == 200
        assert len(r.json()) == 2


class TestEndToEndQuantification:
    """Full workflow: create everything, run Monte Carlo, check dashboard."""

    def _build_full_scenario(self):
        """Set up the complete engagement with all data."""
        eng = create_engagement()
        eid = eng["id"]

        buyer, supplier = add_parties(eid)
        gs = add_goods_service(eid)
        fm1, fm2 = add_failure_modes(eid, gs["id"])
        add_loss_scenarios(eid, fm1["id"], fm2["id"], buyer["id"], supplier["id"])
        add_mitigations(eid, fm1["id"], fm2["id"])

        return eid, eng

    def test_run_quantification(self):
        eid, _ = self._build_full_scenario()

        # Run Monte Carlo with 5000 simulations (fast but enough for stable results)
        r = client.post(f"/api/engagements/{eid}/quantification/run", json={
            "num_simulations": 5000,
        })
        assert r.status_code == 200, r.text
        runs = r.json()

        # Should get 2 runs: unmitigated and mitigated
        assert len(runs) == 2
        unmitigated = next(run for run in runs if not run["is_mitigated"])
        mitigated = next(run for run in runs if run["is_mitigated"])

        # Basic sanity: expected loss > 0
        assert unmitigated["total_expected_loss"] > 0, "Unmitigated EL should be positive"
        assert mitigated["total_expected_loss"] > 0, "Mitigated EL should be positive"

        # Mitigated losses should be lower than unmitigated
        assert mitigated["total_expected_loss"] < unmitigated["total_expected_loss"], \
            f"Mitigated EL ({mitigated['total_expected_loss']:.0f}) should be < unmitigated ({unmitigated['total_expected_loss']:.0f})"

        # VaR should be >= EL (tail is worse than average)
        assert unmitigated["total_var_95"] >= unmitigated["total_expected_loss"]
        assert unmitigated["total_var_99"] >= unmitigated["total_var_95"]

        # Histogram should be populated
        assert len(unmitigated["histogram_bins"]) > 0
        assert len(unmitigated["histogram_counts"]) > 0

        # Per-scenario results should exist
        assert len(unmitigated["results"]) > 0

        # Risk asymmetry ratio: VaR95 / contract value
        # With 500k contract and potential million-dollar breaches, ratio may exceed 1
        assert unmitigated["risk_asymmetry_ratio"] > 0

        print(f"\n{'='*60}")
        print(f"QUANTIFICATION RESULTS — Acme Corp Cloud Hosting")
        print(f"{'='*60}")
        print(f"Simulations: {unmitigated['num_simulations']}")
        print(f"\nUnmitigated:")
        print(f"  Expected Loss:  ${unmitigated['total_expected_loss']:>12,.0f}")
        print(f"  VaR (95%):      ${unmitigated['total_var_95']:>12,.0f}")
        print(f"  TVaR (95%):     ${unmitigated['total_tvar_95']:>12,.0f}")
        print(f"  VaR (99%):      ${unmitigated['total_var_99']:>12,.0f}")
        print(f"  Risk Asymmetry: {unmitigated['risk_asymmetry_ratio']:>12.2f}x")
        print(f"\nMitigated:")
        print(f"  Expected Loss:  ${mitigated['total_expected_loss']:>12,.0f}")
        print(f"  VaR (95%):      ${mitigated['total_var_95']:>12,.0f}")
        print(f"  TVaR (95%):     ${mitigated['total_tvar_95']:>12,.0f}")
        print(f"  VaR (99%):      ${mitigated['total_var_99']:>12,.0f}")
        print(f"  Risk Asymmetry: {mitigated['risk_asymmetry_ratio']:>12.2f}x")
        print(f"\nReduction:")
        el_reduction = unmitigated['total_expected_loss'] - mitigated['total_expected_loss']
        print(f"  EL Reduction:   ${el_reduction:>12,.0f}")
        print(f"  EL % Reduction: {el_reduction / unmitigated['total_expected_loss'] * 100:>11.1f}%")

    def test_dashboard_after_quantification(self):
        eid, eng = self._build_full_scenario()

        # Run quantification first
        r = client.post(f"/api/engagements/{eid}/quantification/run", json={
            "num_simulations": 5000,
        })
        assert r.status_code == 200

        # Now check the dashboard
        r = client.get(f"/api/engagements/{eid}/dashboard")
        assert r.status_code == 200
        dash = r.json()

        assert dash["has_results"] is True
        assert dash["engagement_name"] == eng["name"]
        assert dash["contract_value"] == 500_000
        assert dash["currency"] == "USD"

        # Unmitigated metrics populated
        assert dash["unmitigated_el"] > 0
        assert dash["unmitigated_var_95"] > 0
        assert dash["unmitigated_tvar_95"] > 0

        # Mitigated metrics populated and lower
        assert dash["mitigated_el"] > 0
        assert dash["mitigated_el"] < dash["unmitigated_el"]

        # Top scenarios should exist
        assert len(dash["top_scenarios"]) > 0
        # Contribution percentages should sum to ~100%
        total_contrib = sum(s["contribution_pct"] for s in dash["top_scenarios"])
        assert 95 <= total_contrib <= 105, f"Contributions sum to {total_contrib}%, expected ~100%"

        # Party exposures should include both buyer and supplier
        assert len(dash["party_exposures"]) >= 1

        # Histograms should be present
        assert len(dash["unmitigated_histogram_bins"]) > 0
        assert len(dash["mitigated_histogram_bins"]) > 0

        print(f"\n{'='*60}")
        print(f"DASHBOARD — {dash['engagement_name']}")
        print(f"{'='*60}")
        print(f"\nTop Scenarios:")
        for s in dash["top_scenarios"]:
            print(f"  {s['name']:<35} EL: ${s['expected_loss']:>10,.0f}  ({s['contribution_pct']:.1f}%)")
        print(f"\nParty Exposures:")
        for p in dash["party_exposures"]:
            print(f"  {p['party_name']:<25} EL: ${p['expected_loss']:>10,.0f}  VaR95: ${p['var_95']:>10,.0f}")
        if dash.get("mitigation_summary"):
            print(f"\nMitigation Value:")
            for m in dash["mitigation_summary"]:
                roi_str = f"{m['roi']:.1f}x" if m.get("roi") is not None else "N/A"
                print(f"  {m['name']:<35} Cost: ${m['cost']:>8,.0f}  EL Reduction: ${m['el_reduction']:>8,.0f}  ROI: {roi_str}")

    def test_dashboard_before_quantification(self):
        """Dashboard should return empty/zero metrics before any run."""
        eng = create_engagement()
        r = client.get(f"/api/engagements/{eng['id']}/dashboard")
        assert r.status_code == 200
        dash = r.json()
        assert dash["has_results"] is False
        assert dash["unmitigated_el"] == 0
        assert dash["mitigated_el"] == 0

    def test_excluded_failure_mode_not_in_results(self):
        """If a failure mode is excluded, it should not contribute to results."""
        eng = create_engagement()
        eid = eng["id"]
        buyer, supplier = add_parties(eid)
        gs = add_goods_service(eid)
        fm1, fm2 = add_failure_modes(eid, gs["id"])
        add_loss_scenarios(eid, fm1["id"], fm2["id"], buyer["id"], supplier["id"])

        # Exclude the data breach failure mode
        r = client.patch(f"/api/engagements/{eid}/failure-modes/{fm2['id']}/toggle")
        assert r.json()["is_included"] is False

        # Run with only outage included
        r = client.post(f"/api/engagements/{eid}/quantification/run", json={
            "num_simulations": 5000,
        })
        assert r.status_code == 200
        runs = r.json()
        unmitigated = next(run for run in runs if not run["is_mitigated"])

        # Results should only have scenarios from the outage FM
        for result in unmitigated["results"]:
            if result.get("failure_mode_id"):
                assert result["failure_mode_id"] == fm1["id"], \
                    f"Excluded FM {fm2['id']} should not appear in results"

    def test_quantification_runs_list(self):
        """Multiple runs should be retrievable."""
        eid, _ = self._build_full_scenario()

        # Run twice
        client.post(f"/api/engagements/{eid}/quantification/run", json={"num_simulations": 1000})
        client.post(f"/api/engagements/{eid}/quantification/run", json={"num_simulations": 1000})

        r = client.get(f"/api/engagements/{eid}/quantification/runs")
        assert r.status_code == 200
        assert len(r.json()) == 4  # 2 runs × 2 (unmitigated + mitigated)
