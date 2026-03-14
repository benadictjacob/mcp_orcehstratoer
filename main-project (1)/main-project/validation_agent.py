import ast
import logging
import re
import importlib.util
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Set, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

# =========================================================
# LAYER 1: STRICT SCOPE DISCIPLINE (FOUNDATION)
# =========================================================
# SECURITY DISCLAIMER:
# This system performs RISK DETECTION, not SAFETY GUARANTEES.
# 
# What this validator DOES:
#   ✓ Static AST-based pattern detection
#   ✓ Heuristic risk scoring
#   ✓ Policy violation flagging
#   ✓ Audit trail generation
#
# What this validator DOES NOT:
#   ✗ Execute untrusted code
#   ✗ Simulate runtime behavior
#   ✗ Guarantee code safety
#   ✗ Replace human security review
#
# TRUST MODEL:
#   - All input is treated as potentially malicious
#   - Detection reduces risk probability, not risk existence
#   - Human review is a security feature, not a weakness
# =========================================================

# -------------------------------------------------
# LAYER 3: INPUT HARDENING CONSTANTS
# -------------------------------------------------
MAX_CODE_SIZE_BYTES = 1_000_000  # 1MB max input
MAX_AST_NODES = 50_000           # Prevent parser abuse
MAX_AST_DEPTH = 100              # Prevent deep nesting attacks
ANALYSIS_TIMEOUT_SECONDS = 30    # Prevent DoS via complex input
MAX_LINE_LENGTH = 10_000         # Prevent regex catastrophic backtracking
MAX_LINES = 10_000               # Reasonable file size limit

# -------------------------------------------------
# LAYER 4-5: SANDBOX & RUNTIME POLICY (DOCUMENTATION)
# -------------------------------------------------
# These layers require infrastructure-level implementation.
# This validator provides DETECTION only.
#
# LAYER 4 - SANDBOXED EXECUTION (when execution is added):
#   Requirements:
#   - Separate OS-level boundary (container, microVM)
#   - Options: Docker, Firecracker, gVisor, Kata Containers
#   - Read-only filesystem
#   - No host mounts
#   - No secrets exposed
#   - No default network access
#   - IMPORTANT: Sandbox makes failures survivable, not code safe
#
# LAYER 5 - RUNTIME POLICY ENFORCEMENT (when execution is added):
#   Requirements:
#   - CPU limits (prevent mining, DoS)
#   - Memory limits (prevent exhaustion)
#   - Execution time limits (prevent infinite loops)
#   - Syscall filtering (seccomp profiles)
#   - Network egress control (prevent data exfiltration)
#   - File access allowlists (read-only where possible)
#
# IMPLEMENTATION NOTE:
#   When adding execution capabilities, implement these layers
#   BEFORE enabling any form of code execution.
# -------------------------------------------------

# -------------------------------------------------
# Logging configuration (stderr to protect MCP stdio)
# -------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)

logger = logging.getLogger("validation_agent")

# -------------------------------------------------
# MCP Server Initialization
# -------------------------------------------------
mcp = FastMCP("ValidationAgent")

# -------------------------------------------------
# LAYER 7: Audit & Governance Enums
# -------------------------------------------------
class RiskLevel(str, Enum):
    CRITICAL = "CRITICAL"  # Block deployment, require human
    HIGH = "HIGH"          # Human review mandatory
    MEDIUM = "MEDIUM"      # Review recommended
    LOW = "LOW"            # Safe to proceed
    NONE = "NONE"          # No issues detected


class AuditEvent(BaseModel):
    """Immutable audit record for every validation decision."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    action: str
    input_hash: str  # SHA256 of input (not the input itself)
    risk_level: RiskLevel
    decision: str
    errors_detected: int
    confidence_score: float
    human_required: bool
    metadata: Dict[str, Any] = Field(default_factory=dict)


# -------------------------------------------------
# Data Models
# -------------------------------------------------
class ErrorDetail(BaseModel):
    type: str
    severity: str  # fatal | warning | info
    description: str


class ValidationResult(BaseModel):
    status: str  # PASS | FIXED | BLOCKED
    error_summary: List[ErrorDetail]
    corrected_code: str
    explanations: List[str]
    confidence_score: float
    confidence_breakdown: str  # Explains how confidence was calculated
    human_review_required: bool
    rollback_recommended: bool


# -------------------------------------------------
# Category-Weighted Confidence Scoring
# -------------------------------------------------
class ConfidenceCalculator:
    """
    Calculates confidence as a triage signal based on category-weighted penalties.
    
    Confidence Score Interpretation:
    - 0.9-1.0: High confidence - safe to deploy with minimal review
    - 0.7-0.9: Medium confidence - review recommended
    - 0.5-0.7: Low confidence - human review required
    - 0.0-0.5: Critical - block deployment, manual intervention needed
    """
    
    # Category weights: higher = more severe impact on confidence
    CATEGORY_WEIGHTS = {
        # Critical categories (highest penalty)
        "security": 0.35,
        "syntax": 0.30,
        
        # High-impact categories
        "runtime": 0.20,
        "mcp_specific": 0.18,
        "concurrency": 0.15,
        
        # Medium-impact categories
        "performance": 0.12,
        "logic": 0.10,
        "api_integration": 0.10,
        "dependency": 0.08,
        
        # Low-impact categories (style/informational)
        "semantic": 0.05,
        "compliance": 0.03,
        "logging": 0.02,
        "testability": 0.02,
        "configuration": 0.02,
        "versioning": 0.01,
    }
    
    # Severity multipliers
    SEVERITY_MULTIPLIERS = {
        "fatal": 1.0,    # Full weight applied
        "warning": 0.5,  # Half weight
        "info": 0.1,     # Minimal impact
    }
    
    @classmethod
    def calculate(
        cls, errors: List[ErrorDetail]
    ) -> tuple[float, str]:
        """
        Calculate confidence score with detailed breakdown.
        
        Returns:
            tuple[float, str]: (confidence_score, explanation)
        """
        if not errors:
            return 1.0, "No issues detected. Full confidence."
        
        breakdown_parts: List[str] = []
        total_penalty = 0.0
        
        # Group errors by category for cleaner reporting
        category_penalties: dict[str, float] = {}
        
        for error in errors:
            category = error.type
            severity = error.severity
            
            base_weight = cls.CATEGORY_WEIGHTS.get(category, 0.05)
            multiplier = cls.SEVERITY_MULTIPLIERS.get(severity, 0.5)
            penalty = base_weight * multiplier
            
            category_penalties[category] = category_penalties.get(category, 0) + penalty
            total_penalty += penalty
        
        # Build breakdown explanation
        sorted_categories = sorted(
            category_penalties.items(), key=lambda x: x[1], reverse=True
        )
        
        for category, penalty in sorted_categories:
            count = sum(1 for e in errors if e.type == category)
            breakdown_parts.append(f"{category}: -{penalty:.0%} ({count} issue{'s' if count > 1 else ''})")
        
        # Calculate final confidence (floor at 0.0)
        confidence = max(0.0, 1.0 - total_penalty)
        
        # Build explanation string
        triage_level = cls._get_triage_level(confidence)
        explanation = (
            f"Confidence: {confidence:.0%} [{triage_level}]\n"
            f"Penalties: {' | '.join(breakdown_parts)}\n"
            f"Note: Confidence is a triage signal, not a correctness guarantee."
        )
        
        return round(confidence, 2), explanation
    
    @staticmethod
    def _get_triage_level(confidence: float) -> str:
        if confidence >= 0.9:
            return "HIGH - Safe to deploy"
        elif confidence >= 0.7:
            return "MEDIUM - Review recommended"
        elif confidence >= 0.5:
            return "LOW - Human review required"
        else:
            return "CRITICAL - Block deployment"


# -------------------------------------------------
# Scope-Aware Semantic Analyzer
# -------------------------------------------------
class ScopeTracker(ast.NodeVisitor):
    def __init__(self) -> None:
        self.scopes: List[Set[str]] = [set()]
        self.errors: List[ErrorDetail] = []
        self.builtins = set(dir(__builtins__))
        self.builtins.update({"self", "cls", "mcp"})

    def _is_defined(self, name: str) -> bool:
        return any(name in scope for scope in reversed(self.scopes))

    def _process_function_node(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        scope = {arg.arg for arg in node.args.args}
        self.scopes.append(scope)
        self.generic_visit(node)
        self.scopes.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._process_function_node(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._process_function_node(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.scopes.append(set())
        self.generic_visit(node)
        self.scopes.pop()

    def visit_Import(self, node: ast.Import) -> None:
        for name in node.names:
            self.scopes[-1].add(name.asname or name.name.split(".")[0])

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for name in node.names:
            self.scopes[-1].add(name.asname or name.name)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Store):
            self.scopes[-1].add(node.id)
        elif isinstance(node.ctx, ast.Load):
            if not self._is_defined(node.id) and node.id not in self.builtins:
                self.errors.append(
                    ErrorDetail(
                        type="semantic",
                        severity="info",
                        description=f"Possible use of variable '{node.id}' before assignment",
                    )
                )


# -------------------------------------------------
# LAYER 3: Input Hardening & Abuse Protection
# -------------------------------------------------
class InputValidator:
    """
    Validates and sanitizes input before processing.
    
    Protects against:
    - Denial-of-service attacks
    - Memory exhaustion
    - Parser abuse
    - Regex catastrophic backtracking
    """
    
    @staticmethod
    def validate(code: str) -> tuple[bool, Optional[ErrorDetail]]:
        """
        Validate input before processing.
        
        Returns:
            tuple[bool, Optional[ErrorDetail]]: (is_valid, error_if_any)
        """
        # Check size limits
        if len(code.encode('utf-8')) > MAX_CODE_SIZE_BYTES:
            return False, ErrorDetail(
                type="input_validation",
                severity="fatal",
                description=f"Input exceeds maximum size ({MAX_CODE_SIZE_BYTES} bytes)",
            )
        
        lines = code.split('\n')
        if len(lines) > MAX_LINES:
            return False, ErrorDetail(
                type="input_validation",
                severity="fatal",
                description=f"Input exceeds maximum lines ({MAX_LINES})",
            )
        
        for i, line in enumerate(lines):
            if len(line) > MAX_LINE_LENGTH:
                return False, ErrorDetail(
                    type="input_validation",
                    severity="fatal",
                    description=f"Line {i+1} exceeds maximum length ({MAX_LINE_LENGTH})",
                )
        
        return True, None
    
    @staticmethod
    def validate_ast_complexity(tree: ast.AST) -> tuple[bool, Optional[ErrorDetail]]:
        """Check AST complexity to prevent parser abuse."""
        node_count = sum(1 for _ in ast.walk(tree))
        if node_count > MAX_AST_NODES:
            return False, ErrorDetail(
                type="input_validation",
                severity="fatal",
                description=f"AST complexity exceeds limit ({node_count} > {MAX_AST_NODES} nodes)",
            )
        
        # Check max depth
        def get_depth(node: ast.AST, current: int = 0) -> int:
            max_child_depth = current
            for child in ast.iter_child_nodes(node):
                max_child_depth = max(max_child_depth, get_depth(child, current + 1))
            return max_child_depth
        
        depth = get_depth(tree)
        if depth > MAX_AST_DEPTH:
            return False, ErrorDetail(
                type="input_validation",
                severity="fatal",
                description=f"AST depth exceeds limit ({depth} > {MAX_AST_DEPTH})",
            )
        
        return True, None


# -------------------------------------------------
# Safe Auto-Correction Engine
# -------------------------------------------------
class CorrectionResult(BaseModel):
    """Result of auto-correction attempt."""
    corrected_code: str
    corrections_applied: List[str]
    was_modified: bool


class SafeCorrector:
    """
    Deterministic, safe auto-correction engine.
    
    SAFETY PRINCIPLES:
    1. Only correct patterns that are UNAMBIGUOUSLY wrong
    2. Never correct security issues (those require human review)
    3. All corrections must be syntax-preserving
    4. Each correction is logged for audit
    
    WHAT WE CORRECT:
    ✓ Syntax: Missing colons after def/class/if/for/while/with
    ✓ Syntax: Common keyword typos (dfe→def, calss→class, retrun→return)
    ✓ Syntax: Unclosed parentheses/brackets at end of statement
    ✓ time.sleep() → await asyncio.sleep() in async functions
    ✓ Missing import asyncio when await asyncio.sleep is used
    ✓ print() → logger.info() for production logging
    ✓ Missing logging import when logger is used
    
    WHAT WE DO NOT CORRECT:
    ✗ Security violations (eval, exec, etc.) - BLOCKED
    ✗ Complex syntax errors - Ambiguous intent
    ✗ Logic errors - Ambiguous intent
    ✗ Infinite loops - Could be intentional
    """
    
    # Common keyword typos that are safe to fix
    KEYWORD_TYPOS: Dict[str, str] = {
        "dfe ": "def ",
        "def  ": "def ",
        "deff ": "def ",
        "defn ": "def ",
        "calss ": "class ",
        "clas ": "class ",
        "classs ": "class ",
        "class  ": "class ",
        "retrun ": "return ",
        "reutrn ": "return ",
        "retrn ": "return ",
        "retunr ": "return ",
        "improt ": "import ",
        "ipmort ": "import ",
        "imoprt ": "import ",
        "form ": "from ",  # Only at start of line
        "pritn(": "print(",
        "pirnt(": "print(",
        "prnit(": "print(",
        "asyc ": "async ",
        "aysnc ": "async ",
        "asycn ": "async ",
        "awiat ": "await ",
        "awayt ": "await ",
        "Ture": "True",
        "Flase": "False",
        "Fasle": "False",
        "NOen": "None",
        "Noene": "None",
    }
    
    # Patterns that need colons (regex pattern, description)
    COLON_PATTERNS = [
        (r"^(\s*)(def\s+\w+\s*\([^)]*\))\s*$", "function definition"),
        (r"^(\s*)(async\s+def\s+\w+\s*\([^)]*\))\s*$", "async function definition"),
        (r"^(\s*)(class\s+\w+(?:\s*\([^)]*\))?)\s*$", "class definition"),
        (r"^(\s*)(if\s+.+)\s*$", "if statement"),
        (r"^(\s*)(elif\s+.+)\s*$", "elif statement"),
        (r"^(\s*)(else)\s*$", "else clause"),
        (r"^(\s*)(for\s+.+\s+in\s+.+)\s*$", "for loop"),
        (r"^(\s*)(while\s+.+)\s*$", "while loop"),
        (r"^(\s*)(try)\s*$", "try block"),
        (r"^(\s*)(except(?:\s+\w+)?(?:\s+as\s+\w+)?)\s*$", "except clause"),
        (r"^(\s*)(finally)\s*$", "finally clause"),
        (r"^(\s*)(with\s+.+(?:\s+as\s+\w+)?)\s*$", "with statement"),
    ]
    
    @classmethod
    def fix_syntax_errors(cls, code: str) -> tuple[str, List[str]]:
        """
        Attempt to fix common, unambiguous syntax errors.
        
        Returns:
            tuple[str, List[str]]: (corrected_code, list_of_corrections)
        """
        corrected = code
        corrections: List[str] = []
        
        # -------------------------------------------------
        # FIX-SYN-001: Common keyword typos
        # -------------------------------------------------
        for typo, fix in cls.KEYWORD_TYPOS.items():
            if typo in corrected:
                # Special case: "form " should only be fixed at line start
                if typo == "form ":
                    lines = corrected.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip().startswith("form "):
                            lines[i] = line.replace("form ", "from ", 1)
                            corrections.append(f"[FIX-SYN-001] Fixed typo: 'form' → 'from' (line {i+1})")
                    corrected = '\n'.join(lines)
                else:
                    count = corrected.count(typo)
                    corrected = corrected.replace(typo, fix)
                    corrections.append(f"[FIX-SYN-001] Fixed typo: '{typo.strip()}' → '{fix.strip()}' ({count}x)")
        
        # -------------------------------------------------
        # FIX-SYN-002: Missing colons after statements
        # -------------------------------------------------
        lines = corrected.split('\n')
        modified_lines: List[str] = []
        
        for i, line in enumerate(lines):
            modified_line = line
            
            # Skip if line already ends with colon or is a comment
            if line.rstrip().endswith(':') or line.strip().startswith('#'):
                modified_lines.append(line)
                continue
            
            # Check each colon pattern
            for pattern, desc in cls.COLON_PATTERNS:
                match = re.match(pattern, line)
                if match:
                    # Add missing colon
                    modified_line = line.rstrip() + ':'
                    corrections.append(f"[FIX-SYN-002] Added missing colon after {desc} (line {i+1})")
                    break
            
            modified_lines.append(modified_line)
        
        corrected = '\n'.join(modified_lines)
        
        # -------------------------------------------------
        # FIX-SYN-003: Unclosed brackets at end of simple statements
        # -------------------------------------------------
        lines = corrected.split('\n')
        for i, line in enumerate(lines):
            stripped = line.rstrip()
            
            # Count brackets
            open_parens = stripped.count('(') - stripped.count(')')
            open_brackets = stripped.count('[') - stripped.count(']')
            open_braces = stripped.count('{') - stripped.count('}')
            
            # Only fix simple cases: single unclosed bracket at end of line
            # that looks like a typo (e.g., function call missing closing paren)
            if open_parens == 1 and open_brackets == 0 and open_braces == 0:
                # Check if this looks like a complete statement (ends with value)
                if re.search(r'[\w\d\'")\]]\s*$', stripped):
                    lines[i] = stripped + ')'
                    corrections.append(f"[FIX-SYN-003] Added missing ')' (line {i+1})")
            elif open_brackets == 1 and open_parens == 0 and open_braces == 0:
                if re.search(r'[\w\d\'")\]]\s*$', stripped):
                    lines[i] = stripped + ']'
                    corrections.append(f"[FIX-SYN-003] Added missing ']' (line {i+1})")
            elif open_braces == 1 and open_parens == 0 and open_brackets == 0:
                if re.search(r'[\w\d\'")\]]\s*$', stripped):
                    lines[i] = stripped + '}'
                    corrections.append(f"[FIX-SYN-003] Added missing '}}' (line {i+1})")
        
        corrected = '\n'.join(lines)
        
        # -------------------------------------------------
        # FIX-SYN-004: Common operator typos
        # -------------------------------------------------
        # "= =" should be "==" (but not "= = =" which might be intentional)
        if "= =" in corrected and "= = =" not in corrected:
            corrected = corrected.replace("= =", "==")
            corrections.append("[FIX-SYN-004] Fixed operator typo: '= =' → '=='")
        
        # "! =" should be "!="
        if "! =" in corrected:
            corrected = corrected.replace("! =", "!=")
            corrections.append("[FIX-SYN-004] Fixed operator typo: '! =' → '!='")
        
        return corrected, corrections
    
    @classmethod
    def apply_corrections(cls, code: str, errors: List[ErrorDetail]) -> CorrectionResult:
        """
        Apply safe, deterministic corrections to code.
        
        Returns:
            CorrectionResult with corrected code and list of applied corrections
        """
        corrected = code
        corrections: List[str] = []
        
        # -------------------------------------------------
        # PHASE 1: Try to fix syntax errors FIRST
        # -------------------------------------------------
        has_syntax_error = any(e.type == "syntax" for e in errors)
        if has_syntax_error:
            syntax_fixed, syntax_corrections = cls.fix_syntax_errors(corrected)
            
            # Verify the syntax fix actually works
            try:
                ast.parse(syntax_fixed)
                # Syntax is now valid!
                corrected = syntax_fixed
                corrections.extend(syntax_corrections)
                logger.info(f"Syntax auto-correction successful: {len(syntax_corrections)} fixes applied")
            except (SyntaxError, IndentationError) as e:
                # Syntax fix didn't fully resolve the issue
                # Still apply if it made partial progress
                try:
                    # Check if we made any progress (fewer errors or different error)
                    ast.parse(code)  # Original should fail
                except (SyntaxError, IndentationError) as orig_e:
                    # If the error changed (different line/message), keep the partial fix
                    if str(e) != str(orig_e) and syntax_corrections:
                        corrected = syntax_fixed
                        corrections.extend(syntax_corrections)
                        corrections.append("[FIX-SYN-PARTIAL] Some syntax issues remain - manual review needed")
                        logger.info(f"Partial syntax fix applied: {len(syntax_corrections)} fixes")
        
        # -------------------------------------------------
        # PHASE 2: Apply semantic/style corrections (only if syntax is valid)
        # -------------------------------------------------
        try:
            ast.parse(corrected)
            can_apply_semantic = True
        except (SyntaxError, IndentationError):
            can_apply_semantic = False
        
        if can_apply_semantic:
            # -------------------------------------------------
            # FIX-001: time.sleep() in async context
            # -------------------------------------------------
            if "time.sleep(" in corrected and "async def" in corrected:
                # Only fix if there's a concurrency error flagged
                if any(e.type == "concurrency" for e in errors):
                    # Add asyncio import if missing
                    if "import asyncio" not in corrected and "from asyncio" not in corrected:
                        # Find first import line and add after it
                        lines = corrected.split('\n')
                        for i, line in enumerate(lines):
                            if line.startswith('import ') or line.startswith('from '):
                                lines.insert(i + 1, 'import asyncio')
                                corrections.append("[FIX-001a] Added 'import asyncio'")
                                break
                        else:
                            # No imports found, add at top
                            lines.insert(0, 'import asyncio')
                            corrections.append("[FIX-001a] Added 'import asyncio' at top")
                        corrected = '\n'.join(lines)
                    
                    # Replace time.sleep with await asyncio.sleep
                    corrected = corrected.replace('time.sleep(', 'await asyncio.sleep(')
                    corrections.append("[FIX-001b] Replaced 'time.sleep()' with 'await asyncio.sleep()'")
            
            # -------------------------------------------------
            # FIX-002: print() to logging in production code
            # -------------------------------------------------
            if "print(" in corrected:
                # Check if logging is already imported
                has_logging = "import logging" in corrected or "from logging" in corrected
                
                if not has_logging:
                    # Add logging import
                    lines = corrected.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith('import ') or line.startswith('from '):
                            lines.insert(i + 1, 'import logging')
                            corrections.append("[FIX-002a] Added 'import logging'")
                            break
                    else:
                        lines.insert(0, 'import logging')
                        corrections.append("[FIX-002a] Added 'import logging' at top")
                    corrected = '\n'.join(lines)
                
                # Check if logger is defined
                if "logger = " not in corrected and "logger=" not in corrected:
                    # Add logger definition after imports
                    lines = corrected.split('\n')
                    insert_pos = 0
                    for i, line in enumerate(lines):
                        if line.startswith('import ') or line.startswith('from '):
                            insert_pos = i + 1
                        elif line.strip() and not line.startswith('#') and insert_pos > 0:
                            break
                    lines.insert(insert_pos, 'logger = logging.getLogger(__name__)')
                    corrected = '\n'.join(lines)
                    corrections.append("[FIX-002b] Added logger definition")
                
                # Replace print with logger.info
                corrected = corrected.replace('print(', 'logger.info(')
                corrections.append("[FIX-002c] Replaced 'print()' with 'logger.info()'")
            
            # -------------------------------------------------
            # FIX-003: http:// to https:// for external URLs
            # -------------------------------------------------
            if "http://" in corrected and "localhost" not in corrected and "127.0.0.1" not in corrected:
                if any(e.type == "api_integration" for e in errors):
                    # Only fix obvious external URLs
                    # Match http:// followed by domain (not localhost)
                    pattern = r'http://((?!localhost|127\.0\.0\.1)[a-zA-Z0-9.-]+)'
                    if re.search(pattern, corrected):
                        corrected = re.sub(pattern, r'https://\1', corrected)
                        corrections.append("[FIX-003] Upgraded 'http://' to 'https://' for external URLs")
        
        # -------------------------------------------------
        # Final verification
        # -------------------------------------------------
        if corrections:
            try:
                ast.parse(corrected)
            except (SyntaxError, IndentationError):
                # If we had syntax fixes that worked, keep those but note the issue
                syntax_fixes = [c for c in corrections if c.startswith("[FIX-SYN")]
                if syntax_fixes:
                    # Keep syntax fixes, they might have helped
                    logger.warning("Semantic corrections failed, keeping syntax fixes only")
                    return CorrectionResult(
                        corrected_code=corrected,
                        corrections_applied=syntax_fixes + ["[PARTIAL] Semantic corrections skipped"],
                        was_modified=len(syntax_fixes) > 0,
                    )
                else:
                    # Revert everything
                    logger.warning("Auto-correction introduced syntax error, reverting")
                    return CorrectionResult(
                        corrected_code=code,
                        corrections_applied=["[REVERTED] Corrections caused syntax error"],
                        was_modified=False,
                    )
        
        return CorrectionResult(
            corrected_code=corrected,
            corrections_applied=corrections,
            was_modified=len(corrections) > 0,
        )


# -------------------------------------------------
# LAYER 7: Audit Logger
# -------------------------------------------------
class AuditLogger:
    """Immutable audit trail for all validation decisions."""
    
    _events: List[AuditEvent] = []
    
    @classmethod
    def log(cls, event: AuditEvent) -> None:
        """Record an audit event."""
        cls._events.append(event)
        logger.info(
            f"AUDIT: {event.action} | Risk: {event.risk_level.value} | "
            f"Decision: {event.decision} | Confidence: {event.confidence_score:.0%}"
        )
    
    @classmethod
    def get_events(cls) -> List[AuditEvent]:
        """Get all audit events (read-only copy)."""
        return cls._events.copy()
    
    @classmethod
    def clear(cls) -> None:
        """
        Clear audit log.
        
        ⚠️  WARNING: This method must NEVER be called in production.
        It exists solely for testing purposes. In production environments,
        audit logs must be immutable and preserved for compliance.
        """
        cls._events = []


# -------------------------------------------------
# Validation Agent
# -------------------------------------------------
class ValidationAgent:
    def analyze_syntax(self, code: str) -> List[ErrorDetail]:
        try:
            ast.parse(code)
            return []
        except (SyntaxError, IndentationError) as e:
            return [
                ErrorDetail(
                    type="syntax",
                    severity="fatal",
                    description=f"Syntax error: {e.msg} (line {e.lineno})",
                )
            ]

    def check_semantic_errors(self, code: str) -> List[ErrorDetail]:
        try:
            tree = ast.parse(code)
            tracker = ScopeTracker()
            tracker.visit(tree)
            return tracker.errors
        except Exception:
            return []

    def check_runtime_risks(self, code: str) -> List[ErrorDetail]:
        errors: List[ErrorDetail] = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                    if isinstance(node.right, ast.Constant) and node.right.value == 0:
                        errors.append(
                            ErrorDetail(
                                type="runtime",
                                severity="fatal",
                                description="Division by zero detected",
                            )
                        )
                if isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Constant) and node.value.value is None:
                        errors.append(
                            ErrorDetail(
                                type="runtime",
                                severity="fatal",
                                description="Attribute access on None detected",
                            )
                        )
        except Exception:
            pass
        return errors

    def check_logical_errors(self, code: str) -> List[ErrorDetail]:
        errors: List[ErrorDetail] = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.If):
                    if isinstance(node.test, ast.Constant) and node.test.value is True:
                        errors.append(
                            ErrorDetail(
                                type="logic",
                                severity="warning",
                                description="Condition always evaluates to True",
                            )
                        )
        except Exception:
            pass
        return errors

    def check_api_integration(self, code: str) -> List[ErrorDetail]:
        if "http://" in code and "localhost" not in code:
            return [
                ErrorDetail(
                    type="api_integration",
                    severity="warning",
                    description="Insecure HTTP usage detected",
                )
            ]
        return []

    def check_mcp_specific(self, code: str) -> List[ErrorDetail]:
        errors: List[ErrorDetail] = []
        try:
            tree = ast.parse(code)
            has_fastmcp = False
            has_tool = False

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if (
                        isinstance(node.func, ast.Name)
                        and node.func.id == "FastMCP"
                    ) or (
                        isinstance(node.func, ast.Attribute)
                        and node.func.attr == "FastMCP"
                    ):
                        has_fastmcp = True

                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for deco in node.decorator_list:
                        if (
                            isinstance(deco, ast.Call)
                            and isinstance(deco.func, ast.Attribute)
                            and deco.func.attr == "tool"
                        ):
                            has_tool = True
                            if not isinstance(node, ast.AsyncFunctionDef):
                                errors.append(
                                    ErrorDetail(
                                        type="mcp_specific",
                                        severity="warning",
                                        description=f"MCP tool '{node.name}' should be async",
                                    )
                                )

            if not has_fastmcp or not has_tool:
                errors.append(
                    ErrorDetail(
                        type="mcp_specific",
                        severity="fatal",
                        description="Missing FastMCP initialization or @mcp.tool decorator",
                    )
                )

        except Exception:
            pass

        return errors

    def check_dependency_errors(self, code: str) -> List[ErrorDetail]:
        errors: List[ErrorDetail] = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        mod = name.name.split(".")[0]
                        if importlib.util.find_spec(mod) is None:
                            errors.append(
                                ErrorDetail(
                                    type="dependency",
                                    severity="info",
                                    description=f"Dependency '{mod}' not found locally",
                                )
                            )
        except Exception:
            pass
        return errors

    def check_concurrency_errors(self, code: str) -> List[ErrorDetail]:
        if "time.sleep(" in code and "async def" in code:
            return [
                ErrorDetail(
                    type="concurrency",
                    severity="warning",
                    description="Blocking time.sleep used in async context",
                )
            ]
        return []

    def check_security_errors(self, code: str) -> List[ErrorDetail]:
        """
        LAYER 2: Hardened Static Risk Detection
        
        Detects:
        - Direct dangerous calls (eval, exec, os.system)
        - Indirect/obfuscated patterns (__import__, getattr, builtins)
        - Dangerous capability composition (reflection + IO, network + file)
        - Policy violations (hardcoded secrets)
        
        NOTE: Static detection reduces risk probability, not risk existence.
        """
        errors: List[ErrorDetail] = []
        
        # -------------------------------------------------
        # 2.1 Direct Dangerous Calls
        # -------------------------------------------------
        direct_dangerous = [
            ("eval(", "SEC-001", "Direct eval() execution"),
            ("exec(", "SEC-002", "Direct exec() execution"),
            ("os.system(", "SEC-003", "Direct shell command execution"),
            ("subprocess.Popen(", "SEC-004", "Subprocess with shell access"),
            ("subprocess.call(", "SEC-005", "Subprocess call"),
            ("subprocess.run(", "SEC-006", "Subprocess run"),
            ("compile(", "SEC-007", "Dynamic code compilation"),
        ]
        
        for pattern, rule_id, desc in direct_dangerous:
            if pattern in code:
                errors.append(
                    ErrorDetail(
                        type="security",
                        severity="fatal",
                        description=f"[{rule_id}][DIRECT] {desc}: {pattern}",
                    )
                )
        
        # -------------------------------------------------
        # 2.2 Indirect / Obfuscated Patterns
        # -------------------------------------------------
        obfuscated_patterns = [
            (r"__import__\s*\(", "Dynamic import via __import__"),
            (r"getattr\s*\(\s*__import__", "Obfuscated import via getattr(__import__)"),
            (r"builtins\s*\.\s*eval", "Eval via builtins module"),
            (r"builtins\s*\.\s*exec", "Exec via builtins module"),
            (r"globals\s*\(\s*\)\s*\[", "Dynamic access via globals()"),
            (r"locals\s*\(\s*\)\s*\[", "Dynamic access via locals()"),
            (r"getattr\s*\(.+,\s*['\"]__", "Dunder attribute access via getattr"),
            (r"setattr\s*\(.+,\s*['\"]__", "Dunder attribute mutation via setattr"),
            (r"__builtins__", "Direct builtins access"),
            (r"importlib\.import_module", "Dynamic import via importlib"),
            (r"pickle\.loads?", "Pickle deserialization (arbitrary code execution)"),
            (r"marshal\.loads?", "Marshal deserialization"),
            (r"yaml\.load\s*\([^)]*\)", "Unsafe YAML load (use safe_load)"),
            (r"yaml\.unsafe_load", "Explicitly unsafe YAML load"),
        ]
        
        for pattern, desc in obfuscated_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                errors.append(
                    ErrorDetail(
                        type="security",
                        severity="fatal",
                        description=f"[OBFUSCATED] {desc}",
                    )
                )
        
        # -------------------------------------------------
        # 2.3 Dangerous Capability Composition
        # -------------------------------------------------
        # Reflection + IO = Data exfiltration risk
        has_reflection = bool(re.search(r"getattr|setattr|__dict__|globals|locals", code))
        has_io = bool(re.search(r"open\s*\(|read\s*\(|write\s*\(|socket\.|requests\.|urllib", code))
        has_network = bool(re.search(r"socket\.|requests\.|urllib|httpx|aiohttp", code))
        has_file = bool(re.search(r"open\s*\(|pathlib|shutil\.|os\.path", code))
        
        if has_reflection and has_io:
            errors.append(
                ErrorDetail(
                    type="security",
                    severity="warning",
                    description="[SEC-030][COMPOSITION] Reflection + IO detected - potential data exfiltration",
                )
            )
        
        if has_network and has_file:
            errors.append(
                ErrorDetail(
                    type="security",
                    severity="warning",
                    description="[SEC-031][COMPOSITION] Network + File access - potential data exfiltration",
                )
            )
        
        # -------------------------------------------------
        # 2.4 Policy Violations
        # -------------------------------------------------
        secret_patterns = [
            (r"(api_key|apikey)\s*=\s*['\"][^'\"]{8,}", "SEC-040", "Hardcoded API key"),
            (r"(secret|secret_key)\s*=\s*['\"][^'\"]{8,}", "SEC-041", "Hardcoded secret"),
            (r"(password|passwd|pwd)\s*=\s*['\"][^'\"]{4,}", "SEC-042", "Hardcoded password"),
            (r"(token|auth_token|access_token)\s*=\s*['\"][^'\"]{8,}", "SEC-043", "Hardcoded token"),
            (r"(private_key|priv_key)\s*=\s*['\"]", "SEC-044", "Hardcoded private key"),
            (r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----", "SEC-045", "Embedded private key"),
            (r"-----BEGIN\s+CERTIFICATE-----", "SEC-046", "Embedded certificate"),
        ]
        
        for pattern, rule_id, desc in secret_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                errors.append(
                    ErrorDetail(
                        type="security",
                        severity="fatal",
                        description=f"[{rule_id}][POLICY] {desc}",
                    )
                )
        
        return errors

    def check_performance_errors(self, code: str) -> List[ErrorDetail]:
        if "while True:" in code and all(x not in code for x in ("break", "return")):
            return [
                ErrorDetail(
                    type="performance",
                    severity="fatal",
                    description="Potential infinite loop detected",
                )
            ]
        return []

    def validate_and_correct(
        self,
        generated_code: str,
        execution_logs: Optional[str] = None,
    ) -> ValidationResult:
        """
        Main validation entry point with 7-layer security architecture.
        
        LAYER 1: Scope Discipline - Static analysis only, no execution
        LAYER 3: Input Hardening - Size/complexity limits enforced
        LAYER 6: Human Governance - Flags for human review
        LAYER 7: Audit Trail - All decisions logged
        """
        import hashlib
        start_time = time.time()
        errors: List[ErrorDetail] = []
        
        # Generate input hash for audit (not the input itself)
        input_hash = hashlib.sha256(generated_code.encode()).hexdigest()[:16]
        
        # -------------------------------------------------
        # LAYER 3: Input Validation
        # -------------------------------------------------
        is_valid, input_error = InputValidator.validate(generated_code)
        if not is_valid and input_error:
            errors.append(input_error)
            # Early exit for invalid input
            result = ValidationResult(
                status="BLOCKED",
                error_summary=errors,
                corrected_code=generated_code,
                explanations=["Input validation failed - processing aborted"],
                confidence_score=0.0,
                confidence_breakdown="Input rejected before analysis",
                human_review_required=True,
                rollback_recommended=True,
            )
            # Log audit event
            AuditLogger.log(AuditEvent(
                action="VALIDATE",
                input_hash=input_hash,
                risk_level=RiskLevel.CRITICAL,
                decision="BLOCKED",
                errors_detected=1,
                confidence_score=0.0,
                human_required=True,
                metadata={"reason": "input_validation_failed"},
            ))
            return result
        
        # Validate AST complexity if syntax is valid
        try:
            tree = ast.parse(generated_code)
            is_valid, complexity_error = InputValidator.validate_ast_complexity(tree)
            if not is_valid and complexity_error:
                errors.append(complexity_error)
        except (SyntaxError, IndentationError):
            pass  # Syntax errors handled below
        
        # -------------------------------------------------
        # Run all detection layers
        # -------------------------------------------------
        errors.extend(self.analyze_syntax(generated_code))
        errors.extend(self.check_semantic_errors(generated_code))
        errors.extend(self.check_runtime_risks(generated_code))
        errors.extend(self.check_logical_errors(generated_code))
        errors.extend(self.check_api_integration(generated_code))
        errors.extend(self.check_mcp_specific(generated_code))
        errors.extend(self.check_dependency_errors(generated_code))
        errors.extend(self.check_concurrency_errors(generated_code))
        errors.extend(self.check_security_errors(generated_code))
        errors.extend(self.check_performance_errors(generated_code))

        # -------------------------------------------------
        # Enforce analysis timeout (DoS protection)
        # -------------------------------------------------
        if time.time() - start_time > ANALYSIS_TIMEOUT_SECONDS:
            errors.append(ErrorDetail(
                type="governance",
                severity="fatal",
                description=f"[GOV-001] Analysis exceeded time limit ({ANALYSIS_TIMEOUT_SECONDS}s)",
            ))

        # -------------------------------------------------
        # Deduplicate errors (same type + description = single error)
        # -------------------------------------------------
        errors = list({(e.type, e.description): e for e in errors}.values())

        # -------------------------------------------------
        # LAYER 6: Determine risk level and governance
        # -------------------------------------------------
        fatal = any(e.severity == "fatal" for e in errors)
        security_fatal = any(e.type == "security" and e.severity == "fatal" for e in errors)
        
        # Determine risk level
        if security_fatal:
            risk_level = RiskLevel.CRITICAL
            status = "BLOCKED"
        elif fatal:
            risk_level = RiskLevel.HIGH
            status = "BLOCKED"
        elif any(e.severity == "warning" for e in errors):
            risk_level = RiskLevel.MEDIUM
            status = "PASS"
        elif errors:
            risk_level = RiskLevel.LOW
            status = "PASS"
        else:
            risk_level = RiskLevel.NONE
            status = "PASS"

        # Calculate weighted confidence with explanation
        confidence, confidence_breakdown = ConfidenceCalculator.calculate(errors)
        
        # -------------------------------------------------
        # Safe Auto-Correction (only if NOT security-blocked)
        # -------------------------------------------------
        corrected_code = generated_code
        correction_result: Optional[CorrectionResult] = None
        syntax_was_fixed = False
        
        if not security_fatal:
            correction_result = SafeCorrector.apply_corrections(generated_code, errors)
            if correction_result.was_modified:
                corrected_code = correction_result.corrected_code
                
                # Check if syntax was fixed (any FIX-SYN corrections)
                syntax_fixes = [c for c in correction_result.corrections_applied if "FIX-SYN" in c]
                if syntax_fixes:
                    # Verify the corrected code now parses
                    try:
                        ast.parse(corrected_code)
                        syntax_was_fixed = True
                        # Re-run analysis on corrected code to update error list
                        new_errors: List[ErrorDetail] = []
                        new_errors.extend(self.analyze_syntax(corrected_code))
                        new_errors.extend(self.check_semantic_errors(corrected_code))
                        new_errors.extend(self.check_runtime_risks(corrected_code))
                        new_errors.extend(self.check_logical_errors(corrected_code))
                        new_errors.extend(self.check_api_integration(corrected_code))
                        new_errors.extend(self.check_mcp_specific(corrected_code))
                        new_errors.extend(self.check_dependency_errors(corrected_code))
                        new_errors.extend(self.check_concurrency_errors(corrected_code))
                        new_errors.extend(self.check_security_errors(corrected_code))
                        new_errors.extend(self.check_performance_errors(corrected_code))
                        
                        # Deduplicate new errors
                        new_errors = list({(e.type, e.description): e for e in new_errors}.values())
                        
                        # Update errors and recalculate
                        errors = new_errors
                        confidence, confidence_breakdown = ConfidenceCalculator.calculate(errors)
                        
                        # Recalculate risk level
                        fatal = any(e.severity == "fatal" for e in errors)
                        security_fatal = any(e.type == "security" and e.severity == "fatal" for e in errors)
                        
                        if security_fatal:
                            risk_level = RiskLevel.CRITICAL
                            status = "BLOCKED"
                        elif fatal:
                            risk_level = RiskLevel.HIGH
                            status = "BLOCKED"
                        elif any(e.severity == "warning" for e in errors):
                            risk_level = RiskLevel.MEDIUM
                            status = "FIXED"
                        elif errors:
                            risk_level = RiskLevel.LOW
                            status = "FIXED"
                        else:
                            risk_level = RiskLevel.NONE
                            status = "FIXED"
                            
                    except (SyntaxError, IndentationError):
                        pass  # Syntax fix didn't fully work, keep original status
                
                # Check semantic fixes (non-syntax)
                fixable_types = {"concurrency", "logging", "api_integration", "syntax"}
                remaining_errors = [e for e in errors if e.type not in fixable_types]
                if not any(e.severity == "fatal" for e in remaining_errors) and not syntax_was_fixed:
                    status = "FIXED"
        
        # -------------------------------------------------
        # LAYER 6: Human-in-the-loop governance
        # -------------------------------------------------
        human_required = (
            risk_level in (RiskLevel.CRITICAL, RiskLevel.HIGH) or
            confidence < 0.7 or
            security_fatal
        )
        
        rollback_recommended = confidence < 0.5 or security_fatal
        
        # Build explanations list
        explanations = [
            "DISCLAIMER: This system performs risk detection, not safety guarantees.",
            f"Analysis completed in {(time.time() - start_time) * 1000:.0f}ms",
        ]
        
        if errors:
            explanations.append(f"Detected {len(errors)} issue(s) across {len(set(e.type for e in errors))} categories")
        
        # Add correction explanations
        if correction_result and correction_result.corrections_applied:
            explanations.append(f"AUTO-CORRECTIONS APPLIED ({len(correction_result.corrections_applied)}):")
            explanations.extend(correction_result.corrections_applied)
        
        if human_required:
            explanations.append(f"GOVERNANCE: Human review required (Risk: {risk_level.value})")
        
        if security_fatal:
            explanations.append("SECURITY: Critical security violations detected - deployment blocked")

        result = ValidationResult(
            status=status,
            error_summary=errors,
            corrected_code=corrected_code,
            explanations=explanations,
            confidence_score=confidence,
            confidence_breakdown=confidence_breakdown,
            human_review_required=human_required,
            rollback_recommended=rollback_recommended,
        )
        
        # -------------------------------------------------
        # LAYER 7: Audit logging
        # -------------------------------------------------
        AuditLogger.log(AuditEvent(
            action="VALIDATE",
            input_hash=input_hash,
            risk_level=risk_level,
            decision=status,
            errors_detected=len(errors),
            confidence_score=confidence,
            human_required=human_required,
            metadata={
                "categories": list(set(e.type for e in errors)),
                "analysis_time_ms": round((time.time() - start_time) * 1000),
                "corrections_applied": correction_result.corrections_applied if correction_result else [],
                "was_corrected": correction_result.was_modified if correction_result else False,
            },
        ))
        
        return result


# -------------------------------------------------
# MCP Tool Definition
# -------------------------------------------------
@mcp.tool()
async def validate_code(
    generated_code: str,
) -> str:
    agent = ValidationAgent()
    result = agent.validate_and_correct(generated_code)
    return result.model_dump_json(indent=2)


# -------------------------------------------------
# Server Entry Point
# -------------------------------------------------
def main() -> None:
    sys.stdout.flush()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
