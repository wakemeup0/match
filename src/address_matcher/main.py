from fastapi import FastAPI
from pydantic import BaseModel, Field
from rapidfuzz import fuzz
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor

app = FastAPI(
    title="Address Matcher API",
    description="""
    An API service for comparing and matching similar addresses using string matching algorithms.
    This service helps identify whether two addresses refer to the same location, even when they contain
    minor differences, typos, or variations in formatting.
    """,
    version="1.0.0",
    contact={
        "name": "Wakemeup",
        "email": "mail@wakemeup.rocks",
        "url": "https://github.com/wakemeup0/match",  # Replace with actual repo URL
    },
    license_info={
        "name": "MIT",
    }
)

class AddressPair(BaseModel):
    address1: str = Field(
        description="First address to compare",
        json_schema_extra={"examples": ["123 Main St, Suite 100, New York, NY 10001"]}
    )
    address2: str = Field(
        description="Second address to compare",
        json_schema_extra={"examples": ["123 Main Street, Ste 100, New York, NY 10001"]}
    )
    threshold: Optional[float] = Field(
        default=80.0,
        description="Minimum similarity score (0-100) required to consider addresses as matching",
        ge=0.0,
        le=100.0,
        json_schema_extra={"examples": [80.0]}
    )

class BatchAddressRequest(BaseModel):
    pairs: List[AddressPair] = Field(
        description="List of address pairs to compare",
        min_length=1,
        max_length=1000  # Limiting batch size to prevent overload
    )

class MatchResult(BaseModel):
    similarity: float = Field(
        description="Similarity score between the two addresses (0-100)",
        ge=0.0,
        le=100.0
    )
    is_match: bool = Field(
        description="Whether the addresses are considered a match based on the threshold"
    )
    normalized_address1: str = Field(
        description="First address after normalization"
    )
    normalized_address2: str = Field(
        description="Second address after normalization"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "similarity": 95.5,
                "is_match": True,
                "normalized_address1": "123 main st suite 100 new york ny 10001",
                "normalized_address2": "123 main street ste 100 new york ny 10001"
            }
        }
    }

class BatchMatchResult(BaseModel):
    results: List[MatchResult] = Field(
        description="List of match results for each address pair"
    )
    total_pairs: int = Field(
        description="Total number of address pairs processed"
    )
    average_similarity: float = Field(
        description="Average similarity score across all pairs"
    )

def normalize_address(address: str) -> str:
    """
    Normalize address string by converting to lowercase and removing extra whitespace
    
    Args:
        address (str): The input address string to normalize
        
    Returns:
        str: The normalized address string
    """
    return " ".join(address.lower().split())

def process_address_pair(pair: AddressPair) -> MatchResult:
    """
    Process a single address pair and return the match result
    """
    norm_addr1 = normalize_address(pair.address1)
    norm_addr2 = normalize_address(pair.address2)
    similarity = fuzz.token_sort_ratio(norm_addr1, norm_addr2)
    is_match = similarity >= pair.threshold
    
    return MatchResult(
        similarity=similarity,
        is_match=is_match,
        normalized_address1=norm_addr1,
        normalized_address2=norm_addr2
    )

@app.post(
    "/match/",
    response_model=MatchResult,
    summary="Match two addresses",
    description="""
    Compare two addresses and calculate their similarity score.
    
    Use this endpoint when you need to:
    * Verify if two differently formatted addresses refer to the same location
    * Find potential duplicate addresses in your database
    * Validate address data quality
    """,
    response_description="Detailed match results including similarity score and normalized addresses"
)
async def match_addresses(address_pair: AddressPair) -> MatchResult:
    """
    Compare two addresses and return their similarity score and match status
    """
    return process_address_pair(address_pair)

@app.post(
    "/match/batch/",
    response_model=BatchMatchResult,
    summary="Match multiple pairs of addresses",
    description="""
    Compare multiple pairs of addresses in parallel and calculate their similarity scores.
    
    Use this endpoint when you need to:
    * Process multiple address pairs efficiently
    * Batch verify addresses in bulk
    * Perform large-scale address matching operations
    
    The endpoint uses parallel processing for better performance when handling multiple pairs.
    """,
    response_description="Batch match results including individual pair results and summary statistics"
)
async def batch_match_addresses(request: BatchAddressRequest) -> BatchMatchResult:
    """
    Compare multiple pairs of addresses in parallel and return their match results
    """
    # Create a thread pool for parallel processing
    with ThreadPoolExecutor() as executor:
        # Process address pairs in parallel
        results = list(executor.map(process_address_pair, request.pairs))
    
    # Calculate average similarity
    total_similarity = sum(result.similarity for result in results)
    avg_similarity = total_similarity / len(results)
    
    return BatchMatchResult(
        results=results,
        total_pairs=len(results),
        average_similarity=avg_similarity
    )

@app.get(
    "/",
    summary="API Information",
    description="Get basic information about the Address Matcher API and how to use it",
    response_description="Welcome message and basic usage instructions"
)
async def root():
    return {
        "message": "Welcome to the Address Matcher API",
        "description": "This API helps you compare and match similar addresses using string matching",
        "usage": {
            "single_match": {
                "endpoint": "/match/",
                "method": "POST",
                "example_body": {
                    "address1": "123 Main St, Suite 100, New York, NY 10001",
                    "address2": "123 Main Street, Ste 100, New York, NY 10001",
                    "threshold": 80.0
                }
            },
            "batch_match": {
                "endpoint": "/match/batch/",
                "method": "POST",
                "example_body": {
                    "pairs": [
                        {
                            "address1": "123 Main St, Suite 100, New York, NY 10001",
                            "address2": "123 Main Street, Ste 100, New York, NY 10001",
                            "threshold": 80.0
                        },
                        {
                            "address1": "456 Oak Ave, Chicago, IL 60601",
                            "address2": "456 Oak Avenue, Chicago, IL 60601",
                            "threshold": 80.0
                        }
                    ]
                }
            }
        },
        "documentation": "/docs"
    } 