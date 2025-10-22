import os
import pandas as pd

class QuestionHandler:
    def __init__(self, dataset_path, used_file_path=None):
        self.dataset_path = dataset_path
        self.used_file_path = used_file_path or os.path.join(dataset_path, "used_questions.txt")

        # Ensure dataset folder exists
        os.makedirs(self.dataset_path, exist_ok=True)
        # Ensure used_questions.txt exists
        if not os.path.exists(self.used_file_path):
            open(self.used_file_path, "w").close()

        self.df = self.load_dataset()

    def load_dataset(self):
        # List all CSV files in the dataset folder ONLY
        csv_files = [os.path.join(self.dataset_path, f) for f in os.listdir(self.dataset_path) if f.endswith(".csv")]
        if not csv_files:
            return pd.DataFrame()  # return empty DataFrame if no CSVs

        dataframes = [pd.read_csv(f) for f in csv_files]
        df = pd.concat(dataframes, ignore_index=True)

        # Clean data
        df.columns = df.columns.str.strip()
        df.dropna(subset=["Question_Text", "Answer"], inplace=True)
        df["Question_Type"] = df["Question_Type"].str.strip()
        df["Difficulty"] = df["Difficulty"].str.strip().str.title()
        df["Topic"] = df["Topic"].str.strip()
        return df


    def filter_questions(self, topic=None, q_type=None, difficulty=None):
        filtered = self.df
        if topic:
            filtered = filtered[filtered["Topic"].str.lower() == topic.lower()]
        if q_type:
            filtered = filtered[filtered["Question_Type"].str.lower() == q_type.lower()]
        if difficulty:
            filtered = filtered[filtered["Difficulty"].str.lower() == difficulty.lower()]
        return filtered

    def filter_unused(self, df_filtered):
        if os.path.exists(self.used_file_path):
            with open(self.used_file_path, "r", encoding="utf-8") as f:
                used = f.read().splitlines()
            df_filtered = df_filtered[~df_filtered["Question_Text"].isin(used)]
        return df_filtered

    def mark_used(self, questions):
        with open(self.used_file_path, "a", encoding="utf-8") as f:
            for q in questions:
                f.write(q + "\n")

    def get_random_set(self, topic, num_easy=3, num_medium=3, num_hard=3):
        easy = self.filter_unused(self.filter_questions(topic, difficulty="Easy")).sample(
            n=min(num_easy, len(self.df[self.df["Difficulty"]=="Easy"])),
            replace=False
        ) if not self.df[self.df["Difficulty"]=="Easy"].empty else pd.DataFrame()

        medium = self.filter_unused(self.filter_questions(topic, difficulty="Medium")).sample(
            n=min(num_medium, len(self.df[self.df["Difficulty"]=="Medium"])),
            replace=False
        ) if not self.df[self.df["Difficulty"]=="Medium"].empty else pd.DataFrame()

        hard = self.filter_unused(self.filter_questions(topic, difficulty="Hard")).sample(
            n=min(num_hard, len(self.df[self.df["Difficulty"]=="Hard"])),
            replace=False
        ) if not self.df[self.df["Difficulty"]=="Hard"].empty else pd.DataFrame()

        frames = [df for df in [easy, medium, hard] if not df.empty]
        final_set = pd.concat(frames) if frames else pd.DataFrame(columns=self.df.columns)

        # Mark used questions
        self.mark_used(final_set["Question_Text"].tolist())
        return final_set.sample(frac=1).reset_index(drop=True)
