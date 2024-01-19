from pydantic import EmailStr, HttpUrl

from .core import SSNOlibModel


class Agent(SSNOlibModel):
    """Pydantic Model for https://www.w3.org/ns/prov#Agent

    .. note::

        More than the below parameters are possible but not explicitly defined here.


    Parameters
    ----------
    mbox: EmailStr = None
        Email address (foaf:mbox)
    """
    mbox: EmailStr = None  # foaf:mbox

    def _repr_html_(self) -> str:
        """Returns the HTML representation of the class"""
        return f"{self.__class__.__name__}({self.mbox})"


class Organization(Agent):
    """Pydantic Model for https://www.w3.org/ns/prov#Organization

    .. note::

        More than the below parameters are possible but not explicitly defined here.


    Parameters
    ----------
    mbox: EmailStr = None
        Email address (foaf:mbox)
    """


class Person(Agent):
    """Pydantic Model for https://www.w3.org/ns/prov#Person

    .. note::

        More than the below parameters are possible but not explicitly defined here.


    Parameters
    ----------
    first_name: str = None
        First name (foaf:firstName)
    last_name: str = None
        Last name (foaf:lastName)
    mbox: EmailStr = None
        Email address (foaf:mbox)
    identifier: HttpUrl = None
        Identifier, e.g. ORCID ID (http://w3id.org/nfdi4ing/metadata4ing#identifier)

    Extra fields are possible but not explicitly defined here.
    """
    first_name: str = None  # foaf:firstName
    last_name: str = None  # foaf:lastName
    identifier: HttpUrl = None  # dcterms:identifier

    def _repr_html_(self) -> str:
        """Returns the HTML representation of the class"""
        return f"{self.__class__.__name__}({self.first_name} {self.last_name}, {self.mbox}, {self.identifier})"
