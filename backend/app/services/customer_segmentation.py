import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

from app.services.rfm_analysis import calculate_rfm_segments

def run_kmeans_evaluation(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Run K-Means clustering for K ranges [2, 8].
    Calculates within-cluster sum of squares (inertia) and silhouette scores
    to help choose the optimal cluster size (Elbow & Silhouette methods).
    """
    # 1. Feature Engineering: RFM base
    rfm_df = calculate_rfm_segments(df)
    features = rfm_df[["recency", "frequency", "monetary"]].copy()
    
    # Handle log transform to handle right-skewness of monetary & frequency (standard ML practice)
    # Log transform is crucial for K-means because it assumes symmetric distributions
    features_log = np.log1p(features)
    
    # 2. Scale Features
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features_log)
    
    elbow_data = []
    silhouette_data = []
    
    # Evaluate clusters K from 2 to 8
    max_k = min(len(rfm_df) - 1, 8)
    if max_k < 2:
        return {
            "elbow": [],
            "silhouette": [],
            "message": "Insufficient data points to perform clustering evaluation."
        }
        
    for k in range(2, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(scaled_features)
        
        # Inertia (WCSS)
        elbow_data.append({"k": k, "wcss": float(kmeans.inertia_)})
        
        # Silhouette Score
        score = silhouette_score(scaled_features, kmeans.labels_)
        silhouette_data.append({"k": k, "score": float(score)})
        
    return {
        "elbow": elbow_data,
        "silhouette": silhouette_data
    }

def fit_customer_clusters(df: pd.DataFrame, n_clusters: int = 4) -> Dict[str, Any]:
    """
    Fit K-Means clustering using n_clusters.
    Applies PCA projection for 2D visualization.
    Generates profiles and business labels for each cluster.
    """
    # 1. Base RFM features
    rfm_df = calculate_rfm_segments(df)
    if len(rfm_df) < n_clusters:
        n_clusters = max(2, len(rfm_df))
        
    features = rfm_df[["recency", "frequency", "monetary"]].copy()
    
    # Log transform to reduce skewness
    features_log = np.log1p(features)
    
    # 2. Scale features
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features_log)
    
    # 3. Fit KMeans
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    rfm_df["cluster"] = kmeans.fit_predict(scaled_features)
    
    # 4. Apply PCA projection for scatter plotting
    pca = PCA(n_components=2, random_state=42)
    pca_coords = pca.fit_transform(scaled_features)
    rfm_df["pca_x"] = pca_coords[:, 0]
    rfm_df["pca_y"] = pca_coords[:, 1]
    
    # Explain variance ratio of PCA components
    explained_variance = [float(x) for x in pca.explained_variance_ratio_]
    
    # 5. Profile each cluster to assign business labels
    cluster_profiles = []
    
    # Calculate group averages
    group_means = rfm_df.groupby("cluster").agg({
        "recency": "mean",
        "frequency": "mean",
        "monetary": "mean",
        "customer_id": "count"
    }).rename(columns={"customer_id": "size"})
    
    # Sort clusters by monetary value to assign labels dynamically
    sorted_clusters = group_means.sort_values(by="monetary", ascending=False).index.tolist()
    
    # Dynamic labels depending on size and values
    # Cluster 0 in sorted order (index 0) gets "Premium High Value"
    # Last in sorted order gets "Inactive / Churned"
    # Others get intermediate descriptions
    labels_dict = {}
    for rank_idx, cluster_id in enumerate(sorted_clusters):
        if rank_idx == 0:
            labels_dict[cluster_id] = "Champions (High Value)"
        elif rank_idx == len(sorted_clusters) - 1:
            labels_dict[cluster_id] = "Churned / Inactive"
        elif rank_idx == 1:
            labels_dict[cluster_id] = "Loyal Accounts"
        else:
            labels_dict[cluster_id] = "Mid-Market / At Risk"
            
    rfm_df["business_label"] = rfm_df["cluster"].map(labels_dict)
    
    # Re-build profiles with assigned labels
    for c_id in range(n_clusters):
        row = group_means.loc[c_id]
        cluster_profiles.append({
            "cluster_id": int(c_id),
            "label": labels_dict[c_id],
            "size": int(row["size"]),
            "average_recency": round(float(row["recency"]), 2),
            "average_frequency": round(float(row["frequency"]), 2),
            "average_monetary": round(float(row["monetary"]), 2)
        })
        
    # Format individual customer list for plotting
    customers_list = rfm_df[[
        "customer_id", "customer_name", "recency", "frequency", 
        "monetary", "rfm_score", "cluster", "business_label", "pca_x", "pca_y"
    ]].round(4).to_dict(orient="records")
    
    return {
        "profiles": cluster_profiles,
        "customers": customers_list,
        "pca_variance_ratio": explained_variance
    }
