import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime

@st.cache_data(ttl='6h')
def fetch_github_repository_data(repository="sclebow-iaac/hypera_data_dashboard", since_date=None):
    """
    Fetch repository data from GitHub API with no commit limit
    
    Parameters:
    repository (str): Repository name in format 'owner/repo'
    since_date (str, optional): ISO format date string (YYYY-MM-DD) to filter commits from
    """
    try:
        # Base API URL
        base_url = f"https://api.github.com/repos/{repository}"
        
        # Get repository info
        repo_response = requests.get(base_url)
        if repo_response.status_code != 200:
            return None, f"Error fetching repository data: {repo_response.status_code}"
        
        repo_data = repo_response.json()
        
        # Get all commits with pagination
        all_commits = []
        page = 1
        more_commits = True
        
        while more_commits:
            # Build the commits URL with pagination and optional date filtering
            commits_url = f"{base_url}/commits?per_page=100&page={page}"
            if since_date:
                # Convert date string to proper format if needed
                if isinstance(since_date, str) and len(since_date) == 10:  # YYYY-MM-DD format
                    since_date = f"{since_date}T00:00:00Z"
                commits_url += f"&since={since_date}"
            
            # Fetch commits for current page
            commits_response = requests.get(commits_url)
            
            if commits_response.status_code != 200:
                if page == 1:
                    return repo_data, f"Error fetching commit data: {commits_response.status_code}"
                else:
                    # We've already got some commits, so just break the loop
                    break
            
            page_commits = commits_response.json()
            
            # If we got an empty list or fewer than 100 items, we've reached the end
            if not page_commits or len(page_commits) < 100:
                all_commits.extend(page_commits)
                more_commits = False
            else:
                all_commits.extend(page_commits)
                page += 1
                
            # Add a progress message every few pages
            if page % 5 == 0:
                print(f"Fetched {len(all_commits)} commits so far...")
        
        # Get contributors
        contributors_response = requests.get(f"{base_url}/contributors")
        if contributors_response.status_code != 200:
            return repo_data, all_commits, f"Error fetching contributor data: {contributors_response.status_code}"
        
        contributors_data = contributors_response.json()
        
        # Get pull requests with similar pagination approach
        all_pulls = []
        page = 1
        more_pulls = True
        
        while more_pulls:
            pulls_url = f"{base_url}/pulls?state=all&per_page=100&page={page}"
            pulls_response = requests.get(pulls_url)
            
            if pulls_response.status_code != 200:
                if page == 1:
                    return repo_data, all_commits, contributors_data, f"Error fetching pull request data: {pulls_response.status_code}"
                else:
                    break
            
            page_pulls = pulls_response.json()
            
            if not page_pulls or len(page_pulls) < 100:
                all_pulls.extend(page_pulls)
                more_pulls = False
            else:
                all_pulls.extend(page_pulls)
                page += 1
        
        # If we have a since_date, filter PRs that were created after that date
        if since_date:
            since_datetime = pd.to_datetime(since_date)
            all_pulls = [pr for pr in all_pulls if pd.to_datetime(pr['created_at']) >= since_datetime]
        
        print(f"Fetched total: {len(all_commits)} commits, {len(all_pulls)} pull requests")
        
        return {
            "repository": repo_data,
            "commits": all_commits,
            "contributors": contributors_data,
            "pulls": all_pulls,
            "filter_date": since_date
        }
    except Exception as e:
        return None, f"Error: {str(e)}"

def check_github_rate_limit():
    """Check GitHub API rate limit status"""
    try:
        response = requests.get("https://api.github.com/rate_limit")
        if response.status_code == 200:
            data = response.json()
            core = data.get("resources", {}).get("core", {})
            remaining = core.get("remaining", 0)
            limit = core.get("limit", 0)
            reset_time = datetime.datetime.fromtimestamp(core.get("reset", 0))
            
            return {
                "remaining": remaining,
                "limit": limit,
                "reset_time": reset_time
            }
    except Exception as e:
        return None
    
    return None

def fetch_branch_data(repository):
    """Fetch branch data for a repository"""
    try:
        response = requests.get(f"https://api.github.com/repos/{repository}/branches")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []
    
# Add this helper function
def create_simple_git_graph(filtered_commit_df, author_colors):
    """Create a simplified git graph when enhanced version fails"""
    fig = go.Figure()
    
    # Add main branch line
    fig.add_trace(go.Scatter(
        x=filtered_commit_df["date"],
        y=[0] * len(filtered_commit_df),
        mode="lines",
        line=dict(color="rgba(0,0,255,0.5)", width=2),
        hoverinfo="skip",
        showlegend=False
    ))
    
    # Add commit nodes with author-based coloring
    fig.add_trace(go.Scatter(
        x=filtered_commit_df["date"],
        y=[0] * len(filtered_commit_df),
        mode="markers+text",
        marker=dict(
            color=[author_colors.get(author, "blue") for author in filtered_commit_df["author"]],
            size=12,
            line=dict(color="darkblue", width=1)
        ),
        text=filtered_commit_df["sha"],
        textposition="top center",
        textfont=dict(size=8),
        hovertext=filtered_commit_df.apply(
            lambda row: f"<b>{row['sha']}</b><br>" +
                        f"Author: {row['author']}<br>" +
                        f"Date: {row['date'].strftime('%Y-%m-%d %H:%M')}<br>" +
                        f"Message: {row['message']}",
            axis=1
        ),
        hoverinfo="text",
        showlegend=False
    ))
    
    # Layout customization
    fig.update_layout(
        height=300,
        xaxis_title="Commit Date",
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            range=[-1, 1]
        ),
        plot_bgcolor="rgba(240,240,240,0.2)",
        margin=dict(l=10, r=10, t=10, b=10),
        hovermode="closest"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def run():
    # Add this in the dashboard_metrics_tab section
    rate_limit = check_github_rate_limit()
    if rate_limit:
        with st.expander("GitHub API Rate Limit Status"):
            st.write(f"Remaining requests: {rate_limit['remaining']}/{rate_limit['limit']}")
            st.write(f"Reset time: {rate_limit['reset_time'].strftime('%Y-%m-%d %H:%M:%S %Z')}")

    github_url = "https://github.com/sclebow-iaac/hypera_data_dashboard"
    forked_url = 'https://github.com/specklesystems/specklepy'
    
    # Create a git commit history chart
    st.subheader("Repository Links")

    # Add links to repositories
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"[Dashboard GitHub Repository]({github_url})")
    with col2:
        st.markdown(f"[Forked from SpecklePy Repository on 1/23/2024]({forked_url})")
                    
    # Add date filtering 
    st.subheader("Filter Commits")
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Start Date", 
            value=datetime.date(2025, 1, 1),
            min_value=datetime.date(2020, 1, 1),
            max_value=datetime.date.today()
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.date.today(),
            min_value=datetime.date(2020, 1, 1),
            max_value=datetime.date.today()
        )

    # Format date for API filtering - pass the selected start date to the API call
    since_date_str = start_date.strftime('%Y-%m-%d')

    repository = 'sclebow-iaac/hypera_data_dashboard'
    # Fetch GitHub data with date filtering at the API level
    with st.spinner("Fetching repository data..."):
        github_data = fetch_github_repository_data(repository, since_date=since_date_str)

    if isinstance(github_data, tuple) and len(github_data) > 1 and isinstance(github_data[1], str):
        # Show error message
        st.error(github_data[1])
    else:
        # Extract repository metrics
        repo_data = github_data["repository"]
        commits = github_data["commits"]
        contributors = github_data["contributors"]
        pulls = github_data["pulls"]
        
        # Display repository metrics
        st.subheader("Repository Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Stars", repo_data.get("stargazers_count", 0))
        with col2:
            st.metric("Forks", repo_data.get("forks_count", 0))
        with col3:
            st.metric("Open Issues", repo_data.get("open_issues_count", 0))
        with col4:
            st.metric("Watchers", repo_data.get("subscribers_count", 0))
        
        # Process commit data
        commit_df = pd.DataFrame([
            {
                "date": pd.to_datetime(commit["commit"]["author"]["date"]),
                "author": commit["commit"]["author"]["name"],
                "message": commit["commit"]["message"].split("\n")[0],  # Get first line of commit message
                "sha": commit["sha"][:7]  # Short SHA
            }
            for commit in commits
        ])

        authors = commit_df["author"].unique()
        # Create colors for each author evenly spaced
        author_colors = {}
        for i, author in enumerate(authors):
            author_colors[author] = px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]
        # author_colors = px.colors.qualitative.Plotly[:len(authors)]
        
        if not commit_df.empty:
            # Format end_date with time component for proper filtering
            # Both values need to be in UTC for proper comparison with GitHub dates
            end_timestamp = pd.Timestamp(end_date).replace(hour=23, minute=59, second=59).tz_localize('UTC')
            
            # Now all dates should have matching timezone info
            filtered_commit_df = commit_df[commit_df["date"] <= end_timestamp]
            
            # Show stats about filtered data
            total_commits = len(commit_df)
            filtered_commits = len(filtered_commit_df)
            
            st.markdown(f"Showing **{filtered_commits}** commits out of **{total_commits}** total commits")
            
            if filtered_commit_df.empty:
                st.warning(f"No commits found between {start_date} and {end_date}")
            else:
                # Sort by date
                filtered_commit_df = filtered_commit_df.sort_values("date")
                
                # Commit history visualization
                st.subheader("Commit History")
                
                # Create a figure for commit history
                fig = go.Figure()
                
                # Group by date to count commits per day
                commit_counts = filtered_commit_df.groupby(filtered_commit_df["date"].dt.date).size().reset_index()
                commit_counts.columns = ["date", "count"]
                
                # Group by date and author to count commits per day per author
                author_commit_counts = filtered_commit_df.groupby([
                    filtered_commit_df["date"].dt.date, 
                    filtered_commit_df["author"]
                ]).size().reset_index()
                author_commit_counts.columns = ["date", "author", "count"]
                
                # Add a line for each author
                for author in filtered_commit_df["author"].unique():
                    author_data = author_commit_counts[author_commit_counts["author"] == author]
                    fig.add_trace(go.Scatter(
                        x=author_data["date"],
                        y=author_data["count"],
                        mode="lines+markers",
                        name=author,
                        line=dict(color=author_colors.get(author, "blue"), width=2),
                        marker=dict(size=6),
                    ))
                
                # Add total commits line
                fig.add_trace(go.Scatter(
                    x=commit_counts["date"],
                    y=commit_counts["count"],
                    mode="lines+markers",
                    name="Total Commits",
                    line=dict(color="rgba(0,0,0,0.7)", width=3),
                    marker=dict(size=8),
                ))

                # Update layout
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Number of Commits",
                    height=400,
                    margin=dict(l=10, r=40, t=10, b=10),
                    hovermode="x unified",
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=1.1,
                        xanchor="center",
                        x=0.5,
                        title="Authors",
                    )
                )
                
                st.plotly_chart(fig, use_container_width=True)
                

                commit_graph_col, recent_commits_col = st.columns([2, 1])
                with commit_graph_col:

                    # Create git graph visualization
                    st.subheader("Git Commit Graph")

                    if len(filtered_commit_df) > 0:
                        # Add branch information to the commit data if available
                        try:
                            # Get branch data for the repository
                            branches_data = fetch_branch_data(repository)
                            
                            # Create a lookup of branch tips (the latest commit on each branch)
                            branch_tips = {}
                            for branch in branches_data:
                                branch_name = branch["name"]
                                commit_sha = branch.get("commit", {}).get("sha", "")
                                if commit_sha:
                                    branch_tips[commit_sha] = branch_name
                            
                            # Attempt to get full commit history with parent information
                            # This requires additional API calls to get full commit details
                            commits_with_parents = {}
                            for commit in commits:
                                sha = commit["sha"]
                                parents = [p["sha"] for p in commit.get("parents", [])]
                                commits_with_parents[sha] = {
                                    "sha": sha,
                                    "short_sha": sha[:7],
                                    "parents": parents,
                                    "date": pd.to_datetime(commit["commit"]["author"]["date"]),
                                    "author": commit["commit"]["author"]["name"],
                                    "message": commit["commit"]["message"].split("\n")[0]
                                }
                            
                            # Find branches in the commit graph
                            # Simplistic approach: a commit is on a branch if it's in the path from branch tip to root
                            branches_for_commit = {}
                            main_branch = "main"  # Default to main
                            
                            # Find the main branch name (main or master)
                            for branch in branches_data:
                                if branch["name"] in ["main", "master"]:
                                    main_branch = branch["name"]
                                    break
                            
                            # Sort commits by date
                            sorted_commits = sorted(
                                [commits_with_parents[sha] for sha in commits_with_parents], 
                                key=lambda x: x["date"]
                            )
                            
                            # Create a prettier git graph visualization
                            # Assign y-positions for each commit to show branching
                            commit_positions = {}
                            branch_positions = {main_branch: 0}  # Main branch at y=0
                            current_branches = set([main_branch])
                            max_branch_pos = 0
                            
                            for commit in sorted_commits:
                                sha = commit["sha"]
                                short_sha = commit["short_sha"]
                                
                                # Check if commit is at the tip of any branches
                                branch_name = None
                                for branch_sha, br_name in branch_tips.items():
                                    if sha.startswith(branch_sha) or branch_sha.startswith(sha):
                                        branch_name = br_name
                                        break
                                
                                # Assign position based on branch
                                if branch_name and branch_name not in branch_positions:
                                    max_branch_pos += 1
                                    branch_positions[branch_name] = max_branch_pos
                                    current_branches.add(branch_name)
                                
                                # Assign y position (default to 0 for main branch if we can't determine)
                                y_pos = branch_positions.get(branch_name, 0) if branch_name else 0
                                commit_positions[short_sha] = y_pos
                                
                                # Store branch info for the commit
                                branches_for_commit[short_sha] = branch_name or main_branch
                            
                            # Create the enhanced visualization
                            fig = go.Figure()
                            
                            # Add branch lines
                            for branch_name, y_pos in branch_positions.items():
                                # Get commits on this branch
                                branch_commits = [
                                    commit for commit in sorted_commits 
                                    if branches_for_commit.get(commit["short_sha"]) == branch_name
                                ]
                                
                                if branch_commits:
                                    # For vertical layout, swap x and y coordinates
                                    branch_y = [commit["date"] for commit in branch_commits]
                                    branch_x = [y_pos] * len(branch_commits)
                                    
                                    fig.add_trace(go.Scatter(
                                        y=branch_y,
                                        x=branch_x,
                                        mode="lines",
                                        line=dict(
                                            color=px.colors.qualitative.Plotly[y_pos % len(px.colors.qualitative.Plotly)],
                                            width=2
                                        ),
                                        name=branch_name,
                                        hoverinfo="name",
                                        showlegend=False,
                                    ))

                            # Add merge lines between commits
                            for commit in sorted_commits:
                                if len(commit["parents"]) > 1:  # Merge commit
                                    for parent_sha in commit["parents"]:
                                        parent_short_sha = parent_sha[:7]
                                        if parent_short_sha in commit_positions and commit["short_sha"] in commit_positions:
                                            # Draw merge line from parent to this commit
                                            parent_pos = commit_positions[parent_short_sha]
                                            commit_pos = commit_positions[commit["short_sha"]]
                                            
                                            if parent_pos != commit_pos:  # Only draw if on different branches
                                                # Find parent commit object
                                                parent_commit = next(
                                                    (c for c in sorted_commits if c["short_sha"] == parent_short_sha), 
                                                    None
                                                )
                                                
                                                if parent_commit:
                                                    fig.add_trace(go.Scatter(
                                                        y=[parent_commit["date"], commit["date"]],
                                                        x=[parent_pos, commit_pos],
                                                        mode="lines",
                                                        line=dict(color="rgba(150,150,150,0.5)", width=1, dash="dot"),
                                                        showlegend=False
                                                    ))

                            # Add commits with colored nodes by author
                            for commit in sorted_commits:
                                short_sha = commit["short_sha"]
                                if short_sha in commit_positions:
                                    fig.add_trace(go.Scatter(
                                        y=[commit["date"]],
                                        x=[commit_positions[short_sha]],
                                        mode="markers+text",
                                        marker=dict(
                                            color=author_colors.get(commit["author"], "blue"),
                                            size=12,
                                            line=dict(color="darkblue", width=1)
                                        ),
                                        text=short_sha,
                                        textposition="middle right",  # Text on the right side for vertical layout
                                        textfont=dict(size=8),
                                        hovertext=f"<b>{short_sha}</b><br>" +
                                                f"Branch: {branches_for_commit.get(short_sha, 'unknown')}<br>" +
                                                f"Author: {commit['author']}<br>" +
                                                f"Date: {commit['date'].strftime('%Y-%m-%d %H:%M')}<br>" +
                                                f"Message: {commit['message']}",
                                        hoverinfo="text",
                                        name=commit["author"],
                                        showlegend=False
                                    ))

                            # Layout customization for vertical layout
                            fig.update_layout(
                                height=max(600, min(len(sorted_commits) * 15, 1400)),  # Height based on commit count
                                width=max(500, 100 + (max_branch_pos + 1) * 50),  # Width based on branch count
                                yaxis_title="Commit Date",
                                xaxis=dict(
                                    title="Branches",
                                    tickmode="array",
                                    tickvals=list(branch_positions.values()),
                                    ticktext=list(branch_positions.keys()),
                                    showgrid=True,
                                    gridcolor="rgba(200,200,200,0.2)"
                                ),
                                plot_bgcolor="rgba(250,250,250,1)",
                                margin=dict(l=10, r=50, t=50, b=10),  # Add more right margin for commit text
                                hovermode="closest",
                                legend=dict(
                                    title="Branches",
                                    orientation="h",  # Horizontal legend
                                    yanchor="bottom",
                                    y=1.02,  # Position at the top
                                    xanchor="center",
                                    x=0.5  # Center horizontally
                                )
                            )

                            # Reverse y-axis so that newer commits are at the top
                            fig.update_layout(yaxis=dict(autorange="reversed"))

                            st.plotly_chart(fig, use_container_width=True)
                            
                        except Exception as e:
                            st.warning(f"Could not create enhanced git graph visualization: {str(e)}")
                            # Fall back to simple visualization
                            create_simple_git_graph(filtered_commit_df, author_colors)
                    else:
                        st.info("No commits available to display in the graph.")
                
                with recent_commits_col:                            
                    # Add author legend
                    st.subheader("Commit Authors")

                    for i, (author, color) in enumerate(author_colors.items()):
                        st.markdown(
                            f"<div style='display: flex; align-items: center;'>"
                            f"<div style='width: 12px; height: 12px; background-color: {color}; "
                            f"margin-right: 8px; border-radius: 50%;'></div>"
                            f"{author}</div>",
                            unsafe_allow_html=True
                        )                                # Recent commits table
                
                    # Get branch data
                    branches = fetch_branch_data(repository)
                    branch_names = [branch["name"] for branch in branches]

                    # Display branch information
                    st.subheader("Repository Branches")
                    st.write(f"This repository has {len(branches)} branches:")
                    bullet_text = '\n'.join(['1. ' + branch_name for branch_name in branch_names])
                    st.markdown(bullet_text)

                    st.subheader("10 Most Recent Commits")
                    
                    # Format commit dataframe for display
                    display_df = filtered_commit_df.copy()
                    display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d %H:%M")
                    
                    # Show the most recent 10 commits (reversed order)
                    st.dataframe(
                        display_df[["date", "author", "message", "sha"]].sort_values("date", ascending=False).head(10),
                        use_container_width=True,
                        height=400
                    )
                
                # Contributor analysis within date range
                st.subheader(f"Contributor Analysis ({start_date} to {end_date})")
                
                # Calculate contributions within the filtered date range
                author_counts = filtered_commit_df["author"].value_counts().reset_index()
                author_counts.columns = ["name", "contributions"]
                
                if not author_counts.empty:
                    # Create contributor pie chart for filtered dates
                    fig = px.pie(
                        author_counts,
                        names="name",
                        values="contributions",
                        title="Contribution Distribution",
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Plotly
                    )
                    
                    fig.update_layout(
                        height=400,
                        margin=dict(l=10, r=10, t=50, b=10),
                        showlegend=True,
                        legend_title="Contributors",
                        font_family="Roboto Mono",
                        font_color="#2c3e50"
                    )
                    
                    # Add black border to pie segments
                    fig.update_traces(marker=dict(line=dict(color='#000000', width=2)))
                    
                    col1, col2 = st.columns([3, 2])
                    
                    with col1:
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Calculate stats
                        total_contributors = len(author_counts)
                        total_commits = author_counts["contributions"].sum()
                        avg_commits = total_commits / total_contributors if total_contributors > 0 else 0
                        top_contributor = author_counts.iloc[0]["name"] if not author_counts.empty else "N/A"
                        top_contributions = author_counts.iloc[0]["contributions"] if not author_counts.empty else 0
                        
                        st.metric("Contributors in Period", total_contributors)
                        st.metric("Commits in Period", total_commits)
                        st.metric("Average Commits per Contributor", f"{avg_commits:.1f}")
                        st.metric("Top Contributor", f"{top_contributor} ({top_contributions} commits)")
                else:
                    st.info("No contribution data available for the selected date range.")

        else:
            st.info("No commit data available for this repository.")
        
        # Add commit distribution by weekday
        if not commit_df.empty and not filtered_commit_df.empty:
            st.subheader("Commit Distribution by Weekday")
            
            # Add weekday to filtered dataframe
            filtered_commit_df['weekday'] = filtered_commit_df['date'].dt.day_name()
            
            # Count commits by weekday
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_counts = filtered_commit_df['weekday'].value_counts().reindex(weekday_order).reset_index()
            weekday_counts.columns = ['Weekday', 'Count']
            
            # Create weekday distribution chart
            fig = px.bar(
                weekday_counts,
                x='Weekday',
                y='Count',
                range_y=[0, weekday_counts['Count'].max() * 1.1],
                color='Count',
                color_continuous_scale='Viridis',
                labels={'Count': 'Number of Commits', 'Weekday': 'Day of Week'},
                text='Count'  # Add this to show values on bars
            )
            
            fig.update_layout(
                xaxis_title="Day of Week",
                yaxis_title="Number of Commits",
                height=300,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_family="Roboto Mono",
                font_color="#2c3e50",
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Roboto Mono",
                    font_color="#2c3e50"
                )
            )
            
            # Add black border to bars
            fig.update_traces(
                marker=dict(line=dict(color='#000000', width=2)),
                texttemplate='%{text}',
                textposition='outside'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate which day had the most commits
            most_active_day = weekday_counts.loc[weekday_counts['Count'].idxmax()]
            st.markdown(f"**Most active day of the week:** {most_active_day['Weekday']} with {most_active_day['Count']} commits")

            # Add commit distribution by hour UTC
            st.subheader("Commit Distribution by Hour UTC")

            # Add hour to filtered dataframe
            filtered_commit_df['hour'] = filtered_commit_df['date'].dt.hour

            # Count commits by hour
            hour_counts = filtered_commit_df['hour'].value_counts().sort_index().reset_index()
            hour_counts.columns = ['Hour', 'Count']

            # Create hour distribution chart
            fig = px.bar(
                hour_counts,
                x='Hour',
                y='Count',
                range_y=[0, hour_counts['Count'].max() * 1.1],
                color='Count',
                color_continuous_scale='Viridis',
                labels={'Count': 'Number of Commits', 'Hour': 'Hour of Day (UTC)'},
                text='Count'  # Add this to show values on bars
            )

            fig.update_layout(
                xaxis_title="Hour of Day (UTC)",
                yaxis_title="Number of Commits",
                height=300,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_family="Roboto Mono",
                font_color="#2c3e50",
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Roboto Mono",
                    font_color="#2c3e50"
                )
            )

            # Add black border to bars
            fig.update_traces(
                marker=dict(line=dict(color='#000000', width=2)),
                texttemplate='%{text}',
                textposition='outside'
            )

            st.plotly_chart(fig, use_container_width=True)

            # Add Most Recent Commit by Team Member table
            st.subheader("Most Recent Commit by Team Member")

            # Get the most recent commit for each author
            recent_commits = filtered_commit_df.groupby('author').last().reset_index()
            recent_commits = recent_commits.sort_values('date', ascending=False)[['author', 'date', 'message', 'sha']]
            recent_commits['date'] = recent_commits['date'].dt.strftime('%Y-%m-%d %H:%M')

            recent_commits.columns = ['Author', 'Date', 'Message', 'SHA']

            # Display the table with HTML formatting
            st.dataframe(
                recent_commits,
                use_container_width=True,
                hide_index=True,
            )