"""
Vulnerability Scanning API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_current_user, get_current_admin
from app.models.all_models import User, Domain
from app.services.vulnerability_scanner import get_vulnerability_scanner
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/vulnerabilities", tags=["vulnerabilities"])


@router.post("/scan/{domain_id}")
async def scan_domain_vulnerabilities(
    domain_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Scan a domain for vulnerabilities
    Returns: open ports, CVEs, SSL/TLS issues, security headers, DNS records
    """
    # Get domain
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    try:
        scanner = await get_vulnerability_scanner()
        scan_result = await scanner.scan_domain(domain.url)
        
        return {
            "success": True,
            "domain": domain.url,
            "scan_result": scan_result,
            "timestamp": scan_result["scan_time"]
        }
    except Exception as e:
        logger.error(f"Vulnerability scan error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Scan failed: {str(e)}"
        )


@router.get("/scan/{domain_id}")
async def get_scan_result(
    domain_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get latest vulnerability scan result for a domain
    """
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    try:
        scanner = await get_vulnerability_scanner()
        scan_result = await scanner.scan_domain(domain.url)
        return {"success": True, "data": scan_result}
    except Exception as e:
        logger.error(f"Get scan result error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/scan-all")
async def scan_all_domains(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin only: Scan all domains for vulnerabilities
    """
    domains = db.query(Domain).all()
    
    if not domains:
        raise HTTPException(status_code=404, detail="No domains to scan")
    
    try:
        scanner = await get_vulnerability_scanner()
        results = {}
        
        for domain in domains:
            scan_result = await scanner.scan_domain(domain.url)
            results[domain.url] = scan_result
        
        return {
            "success": True,
            "domains_scanned": len(domains),
            "results": results
        }
    except Exception as e:
        logger.error(f"Bulk vulnerability scan error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Bulk scan failed: {str(e)}"
        )


@router.get("/report/{domain_id}")
async def get_vulnerability_report(
    domain_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a formatted vulnerability report for a domain
    """
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    try:
        scanner = await get_vulnerability_scanner()
        scan_result = await scanner.scan_domain(domain.url)
        
        # Format report
        report = {
            "domain": domain.url,
            "scan_time": scan_result["scan_time"],
            "summary": {
                "open_ports_count": len(scan_result.get("ports", {}).get("open", [])),
                "vulnerabilities_count": len(scan_result.get("vulnerabilities", [])),
                "ssl_rating": scan_result.get("ssl_rating", {}).get("rating", "UNKNOWN"),
                "security_headers_score": scan_result.get("headers", {}).get("score", 0),
                "risk_level": _calculate_risk_level(scan_result)
            },
            "details": scan_result
        }
        
        return {"success": True, "report": report}
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(e)}"
        )


def _calculate_risk_level(scan_result: dict) -> str:
    """
    Calculate overall risk level based on scan results
    Returns: CRITICAL, HIGH, MEDIUM, LOW, MINIMAL
    """
    score = 0
    
    # Check open ports (each adds to risk)
    open_ports = len(scan_result.get("ports", {}).get("open", []))
    score += min(open_ports * 5, 30)
    
    # Check vulnerabilities
    vulns = len(scan_result.get("vulnerabilities", []))
    score += min(vulns * 10, 30)
    
    # Check SSL rating
    ssl_rating = scan_result.get("ssl_rating", {}).get("rating", "F")
    ssl_scores = {"A+": 0, "A": 5, "A-": 10, "B": 20, "C": 30, "D": 40, "E": 50, "F": 60}
    score += ssl_scores.get(ssl_rating, 60)
    
    # Check security headers
    headers_score = scan_result.get("headers", {}).get("score", 0)
    score += max(30 - headers_score * 5, 0)
    
    # Determine risk level
    if score >= 80:
        return "CRITICAL"
    elif score >= 60:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    elif score >= 20:
        return "LOW"
    else:
        return "MINIMAL"
