from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Candidate, CandidateSkill, ProficiencyLevel, Skill, SkillCategory


TAXONOMY: dict[str, list[str]] = {
    "Infrastructure as Code & Configuration": [
        "AWS CloudFormation", "Chef", "OpenStack", "Puppet", "Azure ARM Templates", "Packer"
    ],
    "Source Control Management": [
        "Git", "GitHub", "TFS/VTVS", "Bitbucket", "AWS CodeCommit", "Azure Repos",
        "Google Cloud Source Repositories",
    ],
    "Containers & Orchestration": [
        "Kubernetes (Classic)", "ECR/EKS (AWS)", "ACS/AKS (Azure)", "Mesos", "GCE/GKE (Google)"
    ],
    "Build Management": [
        "Maven (Java)", "MSBuild (.NET)", "AWS CodeBuild", "ANT", "BuildMaster", "UrbanCode Build",
        "Build Concepts",
    ],
    "Continuous Integration": [
        "Maven (Java) CI", "Jenkins", "AWS CodePipeline", "Azure DevOps", "Bamboo", "TeamCity",
        "Google Cloud Build CI/CD",
    ],
    "Artifact Repository Management": ["Nexus", "Artifactory", "NuGet"],
    "Testing & QA": ["Mockito", "TestNG", "Selenium", "Cucumber", "JUnit", "JMeter"],
    "Deployment Automation": ["AWS CodeDeploy", "Octopus Deploy", "Go", "UrbanCode Deploy"],
    "Monitoring & Analysis": [
        "Grafana", "AWS CloudWatch / CloudTrail", "Azure Monitor / Application Insights", "New Relic",
        "Nagios", "Splunk", "Graphite", "Elasticsearch, Logstash, Kibana (ELK)",
    ],
    "Security": [
        "Application Security Concepts", "CyberArk", "AWS Secrets Manager", "Azure Key Vault",
        "GCP Secret Manager",
    ],
    "Consulting": [
        "Assessments", "Due Diligence", "Solution Design & Architecture", "Process Mapping", "Pre-Sales",
        "Other Consulting Skills",
    ],
    "Programming": ["Java / J2EE", ".NET / C# / C++", "Groovy", "Python", "Other Programming Skills"],
    "Backend": ["Databases", "Other Backend Skills"],
    "Scripting": ["PowerShell Scripting", "Linux & Windows Shell Scripting", "Other Scripting Skills"],
}

PROFICIENCIES = [
    (0, "No Exposure", 0),
    (1, "Beginner", 1),
    (2, "Working Knowledge", 2),
    (3, "Advanced", 3),
    (4, "Expert", 4),
]

CANDIDATES: list[tuple[str, str, dict[str, int]]] = [
    ("301001", "Aarav Menon", {"AWS CloudFormation": 3, "ECR/EKS (AWS)": 3, "Jenkins": 2, "Git": 3, "Python": 2}),
    ("301002", "Diya Nair", {"Azure ARM Templates": 3, "ACS/AKS (Azure)": 3, "Azure DevOps": 3, "Azure Repos": 2, "PowerShell Scripting": 2}),
    ("301003", "Rohan Iyer", {"Python": 4, "Databases": 3, "GitHub": 3, "Selenium": 2, "Linux & Windows Shell Scripting": 3}),
    ("301004", "Meera Shah", {"Kubernetes (Classic)": 4, "Grafana": 3, "Elasticsearch, Logstash, Kibana (ELK)": 3, "Git": 2, "Jenkins": 2}),
    ("301005", "Vikram Rao", {"Java / J2EE": 4, "Maven (Java)": 4, "Jenkins": 3, "JUnit": 3, "Nexus": 2}),
    ("301006", "Ananya Das", {"AWS CloudFormation": 2, "AWS CodePipeline": 3, "AWS CodeBuild": 3, "AWS CodeDeploy": 2, "AWS Secrets Manager": 2}),
    ("301007", "Kabir Singh", {"Git": 4, "GitHub": 4, "Bitbucket": 3, "Jenkins": 2, "Bamboo": 2}),
    ("301008", "Isha Thomas", {".NET / C# / C++": 3, "MSBuild (.NET)": 3, "NuGet": 3, "Azure DevOps": 2, "Azure Monitor / Application Insights": 2}),
    ("301009", "Aditya Kumar", {"Puppet": 3, "Chef": 3, "Packer": 2, "AWS CloudFormation": 2, "Linux & Windows Shell Scripting": 3}),
    ("301010", "Nisha Patel", {"Selenium": 4, "Cucumber": 3, "JMeter": 3, "TestNG": 3, "Java / J2EE": 2}),
    ("301011", "Arjun Bose", {"GCE/GKE (Google)": 3, "Google Cloud Build CI/CD": 3, "GCP Secret Manager": 2, "GitHub": 3, "Grafana": 2}),
    ("301012", "Tara Joseph", {"Splunk": 4, "Nagios": 3, "Grafana": 3, "AWS CloudWatch / CloudTrail": 3, "Python": 2}),
    ("301013", "Neel Verma", {"Artifactory": 4, "Nexus": 3, "Maven (Java)": 3, "TeamCity": 2, "Git": 3}),
    ("301014", "Sana Khan", {"Application Security Concepts": 4, "CyberArk": 3, "Azure Key Vault": 3, "AWS Secrets Manager": 2, "Python": 2}),
    ("301015", "Rahul Pillai", {"AWS CloudFormation": 3, "Kubernetes (Classic)": 3, "ECR/EKS (AWS)": 2, "Jenkins": 3, "Grafana": 2}),
    ("301016", "Priya Roy", {"Solution Design & Architecture": 3, "Assessments": 3, "Process Mapping": 2, "Pre-Sales": 2, "Azure DevOps": 2}),
    ("301017", "Dev Malhotra", {"OpenStack": 3, "Puppet": 2, "Kubernetes (Classic)": 2, "Python": 3, "Linux & Windows Shell Scripting": 4}),
    ("301018", "Kavya George", {"Groovy": 3, "Jenkins": 4, "Maven (Java) CI": 2, "GitHub": 3, "Artifactory": 2}),
]


def seed_database(db: Session) -> None:
    if db.scalar(select(SkillCategory.category_id).limit(1)) is not None:
        for proficiency_id, name, rank in PROFICIENCIES:
            if db.get(ProficiencyLevel, proficiency_id) is None:
                db.add(ProficiencyLevel(proficiency_id=proficiency_id, level_name=name, level_rank=rank))
        db.commit()
        return

    categories: dict[str, SkillCategory] = {}
    skills: dict[str, Skill] = {}
    next_skill_id = 1
    for order, (category_name, skill_names) in enumerate(TAXONOMY.items(), start=1):
        category = SkillCategory(category_id=order, category_name=category_name, display_order=order)
        db.add(category)
        categories[category_name] = category
        for name in skill_names:
            skill = Skill(skill_id=next_skill_id, category=category, skill_name=name)
            db.add(skill)
            skills[name] = skill
            next_skill_id += 1

    levels = {}
    for proficiency_id, name, rank in PROFICIENCIES:
        level = ProficiencyLevel(proficiency_id=proficiency_id, level_name=name, level_rank=rank)
        db.add(level)
        levels[rank] = level

    for employee_id, name, profile in CANDIDATES:
        candidate = Candidate(
            employee_id=employee_id,
            full_name=name,
            email=f"{employee_id}@example.pace",
        )
        db.add(candidate)
        for skill_name, rank in profile.items():
            # Ignore accidental seed labels not present in the approved workbook taxonomy.
            if skill_name in skills:
                candidate.skills.append(CandidateSkill(skill=skills[skill_name], proficiency=levels[rank]))

    db.commit()
