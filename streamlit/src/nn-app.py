import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from matplotlib.lines import Line2D
from sklearn.datasets import make_blobs, make_circles, make_moons
from sklearn.metrics import accuracy_score, confusion_matrix, log_loss
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler


st.set_page_config(page_title="MLP Playground", layout="wide")

DATASETS = {
    "Moons": "Two interleaving crescents. Good for showing why nonlinear models matter.",
    "Circles": "Concentric rings. A small network can struggle if capacity is too low.",
    "Gaussian Blobs": "Soft clusters. Often easy enough for simpler models.",
    "XOR": "Opposite quadrants share a class. Great for showing nonlinearity.",
    "Spiral": "A hard pattern that rewards depth, width, and regularization.",
}
ACTIVATIONS = {
    "relu": "Common default that often trains quickly.",
    "tanh": "Smooth and zero-centered, often strong on small examples.",
    "logistic": "Classic sigmoid activation. Useful, but can train more slowly.",
    "identity": "Linear behavior. Helpful for demonstrating underfitting.",
}
COLORS = {0: "#2563eb", 1: "#dc2626"}
MARKERS = {"Train": "o", "Validation": "^", "Test": "s"}


@st.cache_data(show_spinner=False)
def make_dataset(name: str, n_samples: int, noise: float, seed: int):
    rng = np.random.default_rng(seed)
    if name == "Moons":
        X, y = make_moons(n_samples=n_samples, noise=noise, random_state=seed)
    elif name == "Circles":
        X, y = make_circles(n_samples=n_samples, noise=noise, factor=0.45, random_state=seed)
    elif name == "Gaussian Blobs":
        X, y = make_blobs(
            n_samples=n_samples,
            centers=[(-1.4, -1.1), (1.4, 1.1)],
            cluster_std=0.55 + (noise * 2.8),
            random_state=seed,
        )
    elif name == "XOR":
        X = rng.uniform(-1, 1, size=(n_samples, 2))
        X += rng.normal(scale=0.7 * noise, size=X.shape)
        y = ((X[:, 0] > 0) ^ (X[:, 1] > 0)).astype(int)
    elif name == "Spiral":
        half = n_samples // 2
        theta = np.linspace(0, 3.5 * np.pi, half)
        radius = np.linspace(0.1, 1.0, half)
        X0 = np.column_stack((radius * np.cos(theta), radius * np.sin(theta)))
        X1 = np.column_stack((radius * np.cos(theta + np.pi), radius * np.sin(theta + np.pi)))
        X = np.vstack((X0, X1))
        X += rng.normal(scale=0.05 + (noise * 0.35), size=X.shape)
        y = np.array([0] * half + [1] * half)
        if len(X) < n_samples:
            extra = n_samples - len(X)
            X = np.vstack((X, rng.normal(scale=0.15, size=(extra, 2))))
            y = np.concatenate((y, rng.integers(0, 2, size=extra)))
    else:
        raise ValueError(f"Unknown dataset: {name}")
    return X.astype(float), y.astype(int)


def prepare_data(name: str, n_samples: int, noise: float, val_frac: float, test_frac: float, scale: bool, seed: int):
    X, y = make_dataset(name, n_samples, noise, seed)
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X, y, test_size=test_frac, random_state=seed, stratify=y
    )
    inner_val = val_frac / (1 - test_frac)
    X_train_raw, X_val_raw, y_train, y_val = train_test_split(
        X_train_raw, y_train, test_size=inner_val, random_state=seed, stratify=y_train
    )
    scaler = StandardScaler() if scale else None
    if scaler is None:
        X_train, X_val, X_test = X_train_raw.copy(), X_val_raw.copy(), X_test_raw.copy()
    else:
        X_train = scaler.fit_transform(X_train_raw)
        X_val = scaler.transform(X_val_raw)
        X_test = scaler.transform(X_test_raw)
    return {
        "full_raw": X,
        "train_raw": X_train_raw,
        "val_raw": X_val_raw,
        "test_raw": X_test_raw,
        "train": X_train,
        "val": X_val,
        "test": X_test,
        "y_train": y_train,
        "y_val": y_val,
        "y_test": y_test,
        "scaler": scaler,
    }


def safe_loss(y_true, prob):
    return float(log_loss(y_true, np.clip(prob, 1e-6, 1 - 1e-6), labels=[0, 1]))


def clone_state(model: MLPClassifier):
    return {
        "coefs_": [w.copy() for w in model.coefs_],
        "intercepts_": [b.copy() for b in model.intercepts_],
        "classes_": model.classes_.copy(),
        "n_layers_": model.n_layers_,
        "n_outputs_": model.n_outputs_,
        "out_activation_": model.out_activation_,
    }


def restore_state(model: MLPClassifier, state: dict):
    model.coefs_ = [w.copy() for w in state["coefs_"]]
    model.intercepts_ = [b.copy() for b in state["intercepts_"]]
    model.classes_ = state["classes_"].copy()
    model.n_layers_ = state["n_layers_"]
    model.n_outputs_ = state["n_outputs_"]
    model.out_activation_ = state["out_activation_"]


def train_model(
    X_train,
    y_train,
    X_val,
    y_val,
    hidden_layers,
    activation,
    solver,
    learning_rate,
    alpha,
    batch_size,
    epochs,
    feature_dropout,
    early_stopping,
    patience,
    seed,
):
    model = MLPClassifier(
        hidden_layer_sizes=tuple(hidden_layers),
        activation=activation,
        solver=solver,
        learning_rate_init=learning_rate,
        alpha=alpha,
        batch_size=min(batch_size, len(X_train)),
        max_iter=1,
        warm_start=True,
        shuffle=True,
        random_state=seed,
    )
    classes = np.unique(y_train)
    rng = np.random.default_rng(seed)
    best_state = None
    best_epoch = 1
    best_val_loss = float("inf")
    wait = 0
    stopped_early = False
    rows = []

    for epoch in range(1, epochs + 1):
        X_epoch = X_train
        if feature_dropout > 0:
            keep = max(1 - feature_dropout, 1e-6)
            mask = (rng.random(X_train.shape) < keep).astype(float) / keep
            X_epoch = X_train * mask
        if epoch == 1:
            model.partial_fit(X_epoch, y_train, classes=classes)
        else:
            model.partial_fit(X_epoch, y_train)

        train_prob = model.predict_proba(X_train)
        val_prob = model.predict_proba(X_val)
        train_acc = float(accuracy_score(y_train, model.predict(X_train)))
        val_acc = float(accuracy_score(y_val, model.predict(X_val)))
        train_loss = safe_loss(y_train, train_prob)
        val_loss = safe_loss(y_val, val_prob)

        rows.append(
            {
                "Epoch": epoch,
                "Train loss": train_loss,
                "Validation loss": val_loss,
                "Train accuracy": train_acc,
                "Validation accuracy": val_acc,
            }
        )

        if val_loss < best_val_loss - 1e-4:
            best_val_loss = val_loss
            best_epoch = epoch
            best_state = clone_state(model)
            wait = 0
        else:
            wait += 1

        if early_stopping and wait >= patience:
            stopped_early = True
            break

    history = pd.DataFrame(rows)
    if early_stopping and best_state is not None:
        restore_state(model, best_state)
    return {
        "model": model,
        "history": history,
        "best_epoch": best_epoch,
        "epochs_ran": len(history),
        "stopped_early": stopped_early,
    }


def parameter_count(hidden_layers, features=2, outputs=1):
    sizes = [features, *hidden_layers, outputs]
    return int(sum((left + 1) * right for left, right in zip(sizes[:-1], sizes[1:])))


def fit_message(history, train_acc, val_acc, best_epoch, epochs_ran):
    gap = train_acc - val_acc
    val_rise = float(history["Validation loss"].iloc[-1] - history["Validation loss"].min())
    if train_acc < 0.78 and val_acc < 0.78:
        return "Underfitting", "The model is still too simple or has not trained long enough."
    if gap > 0.08 and val_rise > 0.03 and best_epoch < epochs_ran:
        return "Overfitting", "Training keeps improving, but validation performance has started to slip."
    return "Healthy Fit", "Training and validation are moving together in a stable way."


def plot_dataset(data):
    fig, ax = plt.subplots(figsize=(6.2, 5.0))
    for split, X_part, y_part in [
        ("Train", data["train_raw"], data["y_train"]),
        ("Validation", data["val_raw"], data["y_val"]),
        ("Test", data["test_raw"], data["y_test"]),
    ]:
        for label in [0, 1]:
            mask = y_part == label
            ax.scatter(
                X_part[mask, 0],
                X_part[mask, 1],
                s=42,
                c=COLORS[label],
                marker=MARKERS[split],
                edgecolors="white",
                linewidths=0.7,
                alpha=0.9,
            )
    legend = [
        Line2D([0], [0], marker="o", linestyle="", markerfacecolor=COLORS[label], markeredgecolor="white", markersize=8, label=f"Class {label}")
        for label in [0, 1]
    ] + [
        Line2D([0], [0], marker=marker, linestyle="", markerfacecolor="#475569", markeredgecolor="#475569", markersize=8, label=split)
        for split, marker in MARKERS.items()
    ]
    ax.legend(handles=legend, loc="best")
    ax.set_title("Dataset And Splits")
    ax.set_xlabel("Feature 1")
    ax.set_ylabel("Feature 2")
    ax.grid(alpha=0.16)
    fig.tight_layout()
    return fig


def plot_boundary(model, data):
    X = data["full_raw"]
    x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
    y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 240), np.linspace(y_min, y_max, 240))
    grid = np.c_[xx.ravel(), yy.ravel()]
    grid_model = data["scaler"].transform(grid) if data["scaler"] is not None else grid
    prob = model.predict_proba(grid_model)[:, 1].reshape(xx.shape)

    fig, ax = plt.subplots(figsize=(6.2, 5.0))
    contour = ax.contourf(xx, yy, prob, levels=np.linspace(0, 1, 13), cmap="RdBu_r", alpha=0.58)
    ax.contour(xx, yy, prob, levels=[0.5], colors="black", linewidths=1.4)
    for split, X_part, y_part in [
        ("Train", data["train_raw"], data["y_train"]),
        ("Validation", data["val_raw"], data["y_val"]),
        ("Test", data["test_raw"], data["y_test"]),
    ]:
        for label in [0, 1]:
            mask = y_part == label
            ax.scatter(
                X_part[mask, 0],
                X_part[mask, 1],
                s=38,
                c=COLORS[label],
                marker=MARKERS[split],
                edgecolors="white",
                linewidths=0.6,
            )
    fig.colorbar(contour, ax=ax, fraction=0.046, pad=0.04, label="P(class 1)")
    ax.set_title("Learned Decision Boundary")
    ax.set_xlabel("Feature 1")
    ax.set_ylabel("Feature 2")
    ax.grid(alpha=0.10)
    fig.tight_layout()
    return fig


def plot_curves(history, best_epoch):
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.2))
    epochs = history["Epoch"]
    axes[0].plot(epochs, history["Train loss"], label="Train loss", color="#0f766e", linewidth=2.2)
    axes[0].plot(epochs, history["Validation loss"], label="Validation loss", color="#dc2626", linewidth=2.2)
    axes[0].axvline(best_epoch, color="#334155", linestyle="--", label="Best epoch")
    axes[0].set_title("Loss By Epoch")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Log loss")
    axes[0].grid(alpha=0.18)
    axes[0].legend()

    axes[1].plot(epochs, history["Train accuracy"], label="Train accuracy", color="#0f766e", linewidth=2.2)
    axes[1].plot(epochs, history["Validation accuracy"], label="Validation accuracy", color="#dc2626", linewidth=2.2)
    axes[1].axvline(best_epoch, color="#334155", linestyle="--", label="Best epoch")
    axes[1].set_title("Accuracy By Epoch")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Accuracy")
    axes[1].set_ylim(0, 1.02)
    axes[1].grid(alpha=0.18)
    axes[1].legend()
    fig.tight_layout()
    return fig


def plot_confusion(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    fig, ax = plt.subplots(figsize=(4.1, 3.8))
    image = ax.imshow(cm, cmap="Blues")
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    for row in range(2):
        for col in range(2):
            ax.text(col, row, str(cm[row, col]), ha="center", va="center", fontsize=12, fontweight="bold")
    ax.set_xticks([0, 1], labels=["Pred 0", "Pred 1"])
    ax.set_yticks([0, 1], labels=["True 0", "True 1"])
    ax.set_title("Test Confusion Matrix")
    fig.tight_layout()
    return fig


def plot_network(hidden_layers):
    fig, ax = plt.subplots(figsize=(7.2, 3.5))
    sizes = [2, *hidden_layers, 1]
    names = ["Inputs"] + [f"Hidden {i + 1}" for i in range(len(hidden_layers))] + ["Output"]
    xs = np.linspace(0.12, 0.88, len(sizes))
    layers = []
    for x, size in zip(xs, sizes):
        ys = np.linspace(0.18, 0.82, min(size, 6))
        layers.append((x, ys, size))
    for (x1, y1, _), (x2, y2, _) in zip(layers[:-1], layers[1:]):
        for left in y1:
            for right in y2:
                ax.plot([x1, x2], [left, right], color="#cbd5e1", linewidth=0.75)
    for (x, ys, size), name in zip(layers, names):
        ax.scatter(np.repeat(x, len(ys)), ys, s=190, color="#f8fafc", edgecolors="#0f766e", linewidths=1.7, zorder=3)
        if size > 6:
            ax.text(x, 0.50, "...", ha="center", va="center", fontsize=14, color="#475569")
        ax.text(x, -0.02, name, ha="center", va="top", fontsize=10)
        ax.text(x, -0.12, f"{size} units", ha="center", va="top", fontsize=9, color="#475569")
    ax.set_xlim(0.02, 0.98)
    ax.set_ylim(-0.18, 1.0)
    ax.axis("off")
    fig.tight_layout()
    return fig


def plot_run_summary(saved_run):
    model = saved_run["model"]
    data = saved_run["data"]
    history = saved_run["history"]
    best_epoch = saved_run.get("best_epoch", saved_run.get("Best epoch"))
    if best_epoch is None:
        best_epoch = int(history.loc[history["Validation loss"].idxmin(), "Epoch"])

    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.4))

    X = data["full_raw"]
    x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
    y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 220), np.linspace(y_min, y_max, 220))
    grid = np.c_[xx.ravel(), yy.ravel()]
    grid_model = data["scaler"].transform(grid) if data["scaler"] is not None else grid
    prob = model.predict_proba(grid_model)[:, 1].reshape(xx.shape)

    boundary_ax = axes[0]
    contour = boundary_ax.contourf(xx, yy, prob, levels=np.linspace(0, 1, 13), cmap="RdBu_r", alpha=0.58)
    boundary_ax.contour(xx, yy, prob, levels=[0.5], colors="black", linewidths=1.3)
    for split, X_part, y_part in [
        ("Train", data["train_raw"], data["y_train"]),
        ("Validation", data["val_raw"], data["y_val"]),
        ("Test", data["test_raw"], data["y_test"]),
    ]:
        for label in [0, 1]:
            mask = y_part == label
            boundary_ax.scatter(
                X_part[mask, 0],
                X_part[mask, 1],
                s=28,
                c=COLORS[label],
                marker=MARKERS[split],
                edgecolors="white",
                linewidths=0.55,
            )
    fig.colorbar(contour, ax=boundary_ax, fraction=0.046, pad=0.04, label="P(class 1)")
    boundary_ax.set_title("Learned Decision Boundary")
    boundary_ax.set_xlabel("Feature 1")
    boundary_ax.set_ylabel("Feature 2")
    boundary_ax.grid(alpha=0.10)

    loss_ax = axes[1]
    loss_ax.plot(history["Epoch"], history["Train loss"], label="Train loss", color="#0f766e", linewidth=2.2)
    loss_ax.plot(history["Epoch"], history["Validation loss"], label="Validation loss", color="#dc2626", linewidth=2.2)
    loss_ax.axvline(best_epoch, color="#334155", linestyle="--", linewidth=1.2, label="Best epoch")
    loss_ax.set_title("Loss By Epoch")
    loss_ax.set_xlabel("Epoch")
    loss_ax.set_ylabel("Log loss")
    loss_ax.grid(alpha=0.18)
    loss_ax.legend()

    fig.suptitle(saved_run["Label"], y=1.02, fontsize=12)
    fig.tight_layout()
    return fig


def architecture_text(hidden_layers):
    return " -> ".join(["2 inputs", *[str(n) for n in hidden_layers], "1 output"])


def run_label(dataset, hidden_layers, activation, alpha, dropout):
    return f"{dataset} | {activation} | {tuple(hidden_layers)} | alpha={alpha:.0e} | drop={dropout:.2f}"


def main():
    st.session_state.setdefault("saved_runs", [])
    st.session_state.setdefault("run_counter", 0)
    st.title("MLP Playground")
    st.markdown(
        "Explore how data shape, hidden layers, activations, regularization, and training time change what an MLP can learn."
    )
    with st.expander("How To Use This Playground"):
        st.markdown(
            """
            - Start with `Moons` or `Circles`, then move to `Spiral`.
            - Keep the network tiny first so you can spot underfitting.
            - Increase epochs with weak regularization to watch overfitting appear.
            - Compare `relu`, `tanh`, `logistic`, and `identity` on the same pattern.
            - Each click on `Train Model` is saved automatically so you can compare runs over time.
            """
        )

    with st.sidebar.form("controls"):
        train_requested = st.form_submit_button("Train Model")

        st.subheader("Dataset")
        dataset = st.selectbox("Pattern", list(DATASETS.keys()), index=0)
        n_samples = st.slider("Number of samples", 200, 1400, 700, 100)
        noise = st.slider("Noise", 0.00, 0.45, 0.18, 0.01)
        scale = st.checkbox("Standardize inputs", value=True)
        seed = st.number_input("Random seed", 0, 9999, 42, 1)
        st.caption(DATASETS[dataset])

        st.subheader("Architecture")
        layer_count = st.slider("Hidden layers", 1, 4, 2)
        defaults = [8, 8, 6, 4]
        hidden_layers = [st.slider(f"Units in hidden layer {i + 1}", 1, 32, defaults[i], 1) for i in range(layer_count)]
        activation = st.selectbox("Activation", ["relu", "tanh", "logistic", "identity"], index=0)
        st.caption(ACTIVATIONS[activation])

        st.subheader("Training")
        solver = st.selectbox("Optimizer", ["adam", "sgd"], index=0)
        lr_exp = st.slider("Learning rate exponent (10^x)", -4.0, -0.5, -2.0, 0.25)
        alpha_exp = st.slider("L2 regularization exponent (10^x)", -6.0, 0.0, -4.0, 0.5)
        epochs = st.slider("Epochs", 20, 400, 180, 10)
        batch = st.slider("Batch size", 8, 256, 32, 8)
        dropout = st.slider("Feature dropout", 0.0, 0.8, 0.0, 0.05)
        early = st.checkbox("Use early stopping", value=False)
        patience = st.slider("Patience", 3, 40, 12, 1, disabled=not early)

        st.subheader("Splits")
        val_frac = st.slider("Validation fraction", 0.10, 0.30, 0.20, 0.05)
        test_frac = st.slider("Test fraction", 0.10, 0.30, 0.20, 0.05)

    data = prepare_data(dataset, n_samples, noise, val_frac, test_frac, scale, int(seed))
    training = train_model(
        data["train"],
        data["y_train"],
        data["val"],
        data["y_val"],
        hidden_layers,
        activation,
        solver,
        10 ** lr_exp,
        10 ** alpha_exp,
        batch,
        epochs,
        dropout,
        early,
        patience,
        int(seed),
    )
    model = training["model"]
    history = training["history"]
    best_epoch = training["best_epoch"]
    epochs_ran = training["epochs_ran"]

    train_acc = float(accuracy_score(data["y_train"], model.predict(data["train"])))
    val_acc = float(accuracy_score(data["y_val"], model.predict(data["val"])))
    test_acc = float(accuracy_score(data["y_test"], model.predict(data["test"])))
    train_loss = safe_loss(data["y_train"], model.predict_proba(data["train"]))
    val_loss = safe_loss(data["y_val"], model.predict_proba(data["val"]))
    test_loss = safe_loss(data["y_test"], model.predict_proba(data["test"]))
    gap = train_acc - val_acc
    params = parameter_count(hidden_layers)
    fit_label, fit_text = fit_message(history, train_acc, val_acc, best_epoch, epochs_ran)

    if train_requested:
        st.session_state["run_counter"] += 1
        st.session_state["saved_runs"].insert(
            0,
            {
                "Run": st.session_state["run_counter"],
                "Label": f"Run {st.session_state['run_counter']}: {run_label(dataset, hidden_layers, activation, 10 ** alpha_exp, dropout)}",
                "Dataset": dataset,
                "Architecture": str(tuple(hidden_layers)),
                "Activation": activation,
                "Validation accuracy": val_acc,
                "Test accuracy": test_acc,
                "Generalization gap": gap,
                "best_epoch": best_epoch,
                "Best epoch": best_epoch,
                "Parameters": params,
                "history": history.copy(deep=True),
                "data": data,
                "model": model,
            },
        )

    metrics = st.columns(6)
    metrics[0].metric("Train accuracy", f"{train_acc:.3f}")
    metrics[1].metric("Validation accuracy", f"{val_acc:.3f}")
    metrics[2].metric("Test accuracy", f"{test_acc:.3f}")
    metrics[3].metric("Generalization gap", f"{gap:+.3f}")
    metrics[4].metric("Best epoch", str(best_epoch))
    metrics[5].metric("Parameters", f"{params:,}")

    summary_col, details_col = st.columns([1.2, 1.8])
    with summary_col:
        if fit_label == "Overfitting":
            st.warning(f"**{fit_label}**: {fit_text}")
        elif fit_label == "Underfitting":
            st.info(f"**{fit_label}**: {fit_text}")
        else:
            st.success(f"**{fit_label}**: {fit_text}")
        if dropout > 0:
            st.caption(
                "Scikit-learn's `MLPClassifier` does not expose hidden-layer dropout, so this app uses feature dropout to illustrate the regularization idea."
            )
    with details_col:
        st.markdown(
            f"""
            **Current setup**

            - Dataset: `{dataset}` with noise `{noise:.2f}` and `{n_samples}` samples
            - Architecture: `{architecture_text(hidden_layers)}` using `{activation}`
            - Optimizer: `{solver}` with learning rate `{10 ** lr_exp:.4f}`
            - Regularization: `alpha={10 ** alpha_exp:.0e}`, feature dropout `{dropout:.2f}`, early stopping `{early}`
            - Loss snapshot: train `{train_loss:.3f}`, validation `{val_loss:.3f}`, test `{test_loss:.3f}`
            """
        )

    tab1, tab2, tab3, tab4 = st.tabs(["Playground", "Diagnostics", "Compare Runs", "Concept Guide"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.pyplot(plot_dataset(data), use_container_width=True)
        with col2:
            st.pyplot(plot_boundary(model, data), use_container_width=True)
        col3, col4 = st.columns([1.1, 1.4])
        with col3:
            st.pyplot(plot_network(hidden_layers), use_container_width=True)
        with col4:
            st.markdown(
                """
                **Reading the boundary**

                - Blue regions lean toward class 0 and red regions lean toward class 1.
                - The black contour marks the 50% decision boundary.
                - If the boundary is too stiff, the model is likely underfitting.
                - If it curls tightly around training points, the model may be overfitting.
                """
            )

    with tab2:
        curve_col, cm_col = st.columns([1.8, 1.0])
        with curve_col:
            st.pyplot(plot_curves(history, best_epoch), use_container_width=True)
        with cm_col:
            st.pyplot(plot_confusion(data["y_test"], model.predict(data["test"])), use_container_width=True)
        if not early and best_epoch < epochs_ran:
            st.caption(f"Validation loss was best at epoch {best_epoch}, but training ran to epoch {epochs_ran}.")
        elif early and training["stopped_early"]:
            st.caption(f"Early stopping halted training after {epochs_ran} epochs and restored epoch {best_epoch}.")
        st.dataframe(
            history.style.format(
                {
                    "Train loss": "{:.4f}",
                    "Validation loss": "{:.4f}",
                    "Train accuracy": "{:.3f}",
                    "Validation accuracy": "{:.3f}",
                }
            ),
            use_container_width=True,
            height=300,
        )

    with tab3:
        st.caption("Each time you click `Train Model`, the current run is automatically added here with the newest run on top.")
        if st.button("Clear saved runs"):
                st.session_state["saved_runs"] = []
                st.rerun()

        saved = st.session_state["saved_runs"]
        if saved:
            comp = pd.DataFrame(saved)[
                [
                    "Run",
                    "Label",
                    "Dataset",
                    "Architecture",
                    "Activation",
                    "Validation accuracy",
                    "Test accuracy",
                    "Generalization gap",
                    "Best epoch",
                    "Parameters",
                ]
            ]
            for saved_run in saved:
                st.pyplot(plot_run_summary(saved_run), use_container_width=True)
                st.caption(
                    f"Validation accuracy {saved_run['Validation accuracy']:.3f} | "
                    f"Test accuracy {saved_run['Test accuracy']:.3f} | "
                    f"Generalization gap {saved_run['Generalization gap']:+.3f} | "
                    f"Parameters {saved_run['Parameters']:,} | "
                    f"Best epoch {saved_run['Best epoch']}"
                )
                st.divider()
            st.dataframe(
                comp.style.format(
                    {
                        "Validation accuracy": "{:.3f}",
                        "Test accuracy": "{:.3f}",
                        "Generalization gap": "{:+.3f}",
                    }
                ),
                use_container_width=True,
                height=280,
            )
        else:
            st.info("Runs will appear here after you click `Train Model`.")

    with tab4:
        st.markdown(
            """
            **Hidden layers and units**

            More units and more layers increase model capacity. That can help with `XOR` and `Spiral`, but it can also make the model memorize noise.

            **Activation**

            `identity` behaves like a linear model, which makes it useful for demonstrating underfitting. `relu` and `tanh` usually create much richer boundaries.

            **Epochs**

            More epochs lower training loss, but validation loss can eventually rise. That split between the two curves is one of the clearest signs of overfitting.

            **Regularization**

            - `alpha` adds L2 weight decay.
            - Early stopping keeps the model from training far past the best validation point.
            - Feature dropout in this app is a teaching-friendly stand-in for dropout because sklearn does not provide hidden-layer dropout.

            **Try these experiments**

            - Use `identity` on `Moons` and notice how the boundary stays too simple.
            - Try `Spiral` with one tiny hidden layer, then add width and another layer.
            - Turn epochs up and `alpha` down to create visible overfitting.
            - Turn on early stopping and compare the validation curve.
            """
        )


if __name__ == "__main__":
    main()
